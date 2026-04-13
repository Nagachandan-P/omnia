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

"""FastAPI dependency providers for Deploy API."""

from fastapi import Depends
from sqlalchemy.orm import Session

from api.dependencies import (
    get_db_session,
    _create_sql_job_repo,
    _create_sql_stage_repo,
    _create_sql_audit_repo,
    _create_sql_image_group_repo,
    _ENV,
)
from orchestrator.deploy.use_cases.deploy_use_case import DeployUseCase


def _get_container():
    """Lazy import of container to avoid circular imports."""
    from container import container  # pylint: disable=import-outside-toplevel
    return container


def get_deploy_use_case(
    db_session: Session = Depends(get_db_session),
) -> DeployUseCase:
    """Provide deploy use case with shared session in prod."""
    if _ENV == "prod":
        container = _get_container()
        return DeployUseCase(
            job_repo=_create_sql_job_repo(db_session),
            stage_repo=_create_sql_stage_repo(db_session),
            audit_repo=_create_sql_audit_repo(db_session),
            image_group_repo=_create_sql_image_group_repo(db_session),
            queue_service=container.deploy_queue_service(),
            uuid_generator=container.uuid_generator(),
        )
    return _get_container().deploy_use_case()
