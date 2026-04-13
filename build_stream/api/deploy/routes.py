# Copyright 2026 Dell Inc. or its subsidiaries. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""FastAPI routes for deploy stage operations."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from api.deploy.dependencies import get_deploy_use_case, _get_container
from api.dependencies import verify_token, require_job_write
from api.deploy.schemas import (
    DeployRequest,
    DeployResponse,
    DeployErrorResponse,
)
from api.logging_utils import log_secure_info
from core.image_group.exceptions import (
    ImageGroupMismatchError,
    ImageGroupNotFoundError,
    InvalidStateTransitionError as ImageGroupInvalidStateTransitionError,
)
from core.jobs.exceptions import (
    JobNotFoundError,
    UpstreamStageNotCompletedError,
)
from core.jobs.value_objects import ClientId, CorrelationId, JobId
from core.validate.exceptions import (
    ValidationExecutionError,
)
from orchestrator.deploy.commands.deploy_command import DeployCommand
from orchestrator.deploy.use_cases.deploy_use_case import DeployUseCase

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["Deploy"])


def _build_error_response(
    error_code: str,
    message: str,
    correlation_id: str,
) -> DeployErrorResponse:
    return DeployErrorResponse(
        error=error_code,
        message=message,
        correlation_id=correlation_id,
        timestamp=datetime.now(timezone.utc).isoformat() + "Z",
    )


def _get_deploy_correlation_id(x_correlation_id=None):
    """Get or generate correlation ID."""
    container = _get_container()
    generator = container.uuid_generator()
    if x_correlation_id:
        try:
            return CorrelationId(x_correlation_id)
        except ValueError:
            pass
    return CorrelationId(str(generator.generate()))


@router.post(
    "/{job_id}/stages/deploy",
    response_model=DeployResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Initiate deploy stage",
    description="Initiates deployment of a previously built Image Group to target nodes.",
    responses={
        202: {"description": "Stage accepted", "model": DeployResponse},
        400: {"description": "Invalid request", "model": DeployErrorResponse},
        401: {"description": "Unauthorized", "model": DeployErrorResponse},
        404: {"description": "Job or ImageGroup not found", "model": DeployErrorResponse},
        409: {"description": "ImageGroup mismatch", "model": DeployErrorResponse},
        412: {"description": "Precondition failed", "model": DeployErrorResponse},
        500: {"description": "Internal error", "model": DeployErrorResponse},
    },
)
def create_deploy(
    job_id: str,
    request_body: DeployRequest,
    token_data: dict = Depends(verify_token),
    use_case: DeployUseCase = Depends(get_deploy_use_case),
    _: None = Depends(require_job_write),
) -> DeployResponse:
    """Initiate deployment for a previously built Image Group."""
    client_id = ClientId(token_data["client_id"])

    # Generate correlation ID
    correlation_id = _get_deploy_correlation_id()

    logger.info(
        "Deploy request: job_id=%s, client_id=%s, correlation_id=%s, image_group_id=%s",
        job_id,
        client_id.value,
        correlation_id.value,
        request_body.image_group_id,
    )

    try:
        validated_job_id = JobId(job_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=_build_error_response(
                "INVALID_JOB_ID",
                f"Invalid job_id format: {job_id}",
                correlation_id.value,
            ).model_dump(),
        ) from exc

    try:
        command = DeployCommand(
            job_id=validated_job_id,
            client_id=client_id,
            correlation_id=correlation_id,
            image_group_id=request_body.image_group_id,
        )
        result = use_case.execute(command)

        return DeployResponse(
            job_id=result.job_id,
            stage=result.stage_name,
            status=result.status,
            submitted_at=result.submitted_at,
            image_group_id=result.image_group_id,
            correlation_id=result.correlation_id,
        )

    except JobNotFoundError as exc:
        logger.warning("Job not found: %s", job_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_build_error_response(
                "JOB_NOT_FOUND", exc.message, correlation_id.value,
            ).model_dump(),
        ) from exc

    except ImageGroupNotFoundError as exc:
        logger.warning("ImageGroup not found for job: %s", job_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=_build_error_response(
                "IMAGE_GROUP_NOT_FOUND", str(exc), correlation_id.value,
            ).model_dump(),
        ) from exc

    except ImageGroupMismatchError as exc:
        log_secure_info(
            "warning",
            f"ImageGroup mismatch for job {job_id}",
            str(correlation_id.value),
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=_build_error_response(
                "IMAGEGROUP_MISMATCH", str(exc), correlation_id.value,
            ).model_dump(),
        ) from exc

    except ImageGroupInvalidStateTransitionError as exc:
        log_secure_info(
            "warning",
            f"Invalid state transition for job {job_id}",
            str(correlation_id.value),
        )
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=_build_error_response(
                "PRECONDITION_FAILED", str(exc), correlation_id.value,
            ).model_dump(),
        ) from exc

    except UpstreamStageNotCompletedError as exc:
        log_secure_info(
            "warning",
            f"Deploy failed: upstream stage not completed for job {job_id}",
            str(correlation_id.value),
        )
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail=_build_error_response(
                "UPSTREAM_STAGE_NOT_COMPLETED", exc.message, correlation_id.value,
            ).model_dump(),
        ) from exc

    except ValidationExecutionError as exc:
        log_secure_info(
            "error",
            f"Deploy execution error for job {job_id}",
            str(correlation_id.value),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_build_error_response(
                "DEPLOY_EXECUTION_ERROR", exc.message, correlation_id.value,
            ).model_dump(),
        ) from exc

    except Exception as exc:
        logger.exception("Unexpected error creating deploy stage")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=_build_error_response(
                "INTERNAL_ERROR", "An unexpected error occurred", correlation_id.value,
            ).model_dump(),
        ) from exc
