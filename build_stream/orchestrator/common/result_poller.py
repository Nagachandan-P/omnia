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

"""Common result poller for processing playbook execution results from NFS queue.

This module provides a shared ResultPoller that can be used by all stage APIs
(local_repo, build_image, validate_image_on_test, etc.) to poll the NFS result
queue and update stage states accordingly.

Enhanced (S1-4 Part B): On build-image success, creates ImageGroup (BUILT)
and Image records from catalog metadata persisted during parse-catalog.
"""

import json
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from api.logging_utils import log_secure_info

from core.image_group.entities import Image, ImageGroup
from core.image_group.repositories import ImageGroupRepository, ImageRepository
from core.image_group.value_objects import ImageGroupId, ImageGroupStatus
from core.artifacts.interfaces import ArtifactMetadataRepository, ArtifactStore
from core.artifacts.value_objects import ArtifactKind
from core.jobs.entities import AuditEvent
from core.jobs.entities.stage import StageState
from core.jobs.repositories import (
    AuditEventRepository,
    JobRepository,
    StageRepository,
    UUIDGenerator,
)
from core.jobs.services import JobStateHelper
from core.jobs.value_objects import JobId, StageName
from core.localrepo.entities import PlaybookResult
from core.localrepo.services import PlaybookQueueResultService

logger = logging.getLogger(__name__)


class ResultPoller:
    """Common poller for processing playbook execution results.

    This poller monitors the NFS result queue and processes results
    by updating stage states and emitting audit events. It handles
    results from all stage types (local_repo, build_image,
    validate_image_on_test, etc.).

    Attributes:
        result_service: Service for polling NFS result queue.
        job_repo: Job repository for updating job states.
        stage_repo: Stage repository for updating stage states.
        audit_repo: Audit event repository for emitting events.
        uuid_generator: UUID generator for event IDs.
        poll_interval: Interval in seconds between polls.
        running: Flag indicating if poller is running.
    """

    def __init__(
        self,
        result_service: PlaybookQueueResultService,
        job_repo: JobRepository,
        stage_repo: StageRepository,
        audit_repo: AuditEventRepository,
        uuid_generator: UUIDGenerator,
        poll_interval: int = 5,
        image_group_repo: ImageGroupRepository = None,
        image_repo: ImageRepository = None,
        artifact_store: ArtifactStore = None,
        artifact_metadata_repo: ArtifactMetadataRepository = None,
    ) -> None:  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Initialize result poller.

        Args:
            result_service: Service for polling NFS result queue.
            job_repo: Job repository implementation.
            stage_repo: Stage repository implementation.
            audit_repo: Audit event repository implementation.
            uuid_generator: UUID generator for identifiers.
            poll_interval: Interval in seconds between polls (default: 5).
            image_group_repo: ImageGroup repository for build-image completion.
            image_repo: Image repository for build-image completion.
            artifact_store: Artifact store for retrieving catalog metadata.
            artifact_metadata_repo: Artifact metadata repo for finding artifacts.
        """
        self._result_service = result_service
        self._job_repo = job_repo
        self._stage_repo = stage_repo
        self._audit_repo = audit_repo
        self._uuid_generator = uuid_generator
        self._poll_interval = poll_interval
        self._image_group_repo = image_group_repo
        self._image_repo = image_repo
        self._artifact_store = artifact_store
        self._artifact_metadata_repo = artifact_metadata_repo
        self._running = False
        self._task = None

    async def start(self) -> None:
        """Start the result poller."""
        if self._running:
            logger.warning("Result poller is already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())
        logger.info("Result poller started with interval=%ds", self._poll_interval)

    async def stop(self) -> None:
        """Stop the result poller."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Result poller stopped")

    async def _poll_loop(self) -> None:
        """Main polling loop."""
        while self._running:
            try:
                processed_count = self._result_service.poll_results(
                    callback=self._on_result_received
                )
                if processed_count > 0:
                    logger.info("Processed %d playbook results", processed_count)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("Error polling results: %s", exc)

            await asyncio.sleep(self._poll_interval)

    def _on_result_received(self, result: PlaybookResult) -> None:
        """Handle received playbook result.

        Args:
            result: Playbook execution result from NFS queue.
        """
        try:
            # Find stage
            stage_name = StageName(result.stage_name)
            stage = self._stage_repo.find_by_job_and_name(result.job_id, stage_name)

            if stage is None:
                logger.error(
                    "Stage not found for result: job_id=%s, stage=%s",
                    result.job_id,
                    result.stage_name,
                )
                return

            # Update stage based on result
            # Check if stage is already in terminal state (e.g., after service restart)
            if stage.stage_state in {StageState.COMPLETED, StageState.FAILED, StageState.CANCELLED}:
                logger.info(
                    "Stage already in terminal state: job_id=%s, stage=%s, state=%s",
                    result.job_id,
                    result.stage_name,
                    stage.stage_state,
                )
                # Return early - service will archive the result file automatically
                return

            if result.status == "success":
                stage.complete()
                logger.info(
                    "Stage completed: job_id=%s, stage=%s",
                    result.job_id,
                    result.stage_name,
                )

                # S1-4 Part B: On build-image success, create ImageGroup + Images
                if self._is_build_image_stage(result.stage_name):
                    self._on_build_image_success(result)

                # Check if this is the final stage (validate-image-on-test)
                # If so, mark the job as completed
                if result.stage_name == "validate-image-on-test":
                    JobStateHelper.handle_job_completion(
                        job_repo=self._job_repo,
                        audit_repo=self._audit_repo,
                        uuid_generator=self._uuid_generator,
                        job_id=JobId(result.job_id),
                        correlation_id=result.request_id.value if hasattr(result.request_id, 'value') else str(result.request_id),
                        client_id=str(result.job_id),
                    )
            else:
                error_code = result.error_code or "PLAYBOOK_FAILED"
                error_summary = result.error_summary or "Playbook execution failed"
                stage.fail(error_code=error_code, error_summary=error_summary)
                logger.warning(
                    "Stage failed: job_id=%s, stage=%s, error=%s",
                    result.job_id,
                    result.stage_name,
                    error_code,
                )

                # Update job state to FAILED when stage fails
                JobStateHelper.handle_stage_failure(
                    job_repo=self._job_repo,
                    audit_repo=self._audit_repo,
                    uuid_generator=self._uuid_generator,
                    job_id=JobId(result.job_id),
                    stage_name=result.stage_name,
                    error_code=error_code,
                    error_summary=error_summary,
                    correlation_id=result.request_id.value if hasattr(result.request_id, 'value') else str(result.request_id),
                    client_id=str(result.job_id),
                )

            # Update log file path if available
            if result.log_file_path:
                stage.log_file_path = result.log_file_path
                logger.info(
                    "Updated stage log path: job_id=%s, stage=%s",
                    result.job_id,
                    result.stage_name,
                )

            # Save updated stage
            self._stage_repo.save(stage)

            # Emit audit event
            event = AuditEvent(
                event_id=str(self._uuid_generator.generate()),
                job_id=result.job_id,
                event_type="STAGE_COMPLETED" if result.status == "success" else "STAGE_FAILED",
                correlation_id=result.request_id,
                client_id=result.job_id,  # Using job_id as client_id placeholder
                timestamp=datetime.now(timezone.utc),
                details={
                    "stage_name": result.stage_name,
                    "status": result.status,
                    "duration_seconds": result.duration_seconds,
                    "exit_code": result.exit_code,
                },
            )
            self._audit_repo.save(event)

            # Commit both repositories if using SQL
            # Note: Each repository may have its own session, so commit both
            if hasattr(self._stage_repo, 'session'):
                self._stage_repo.session.commit()
            if hasattr(self._audit_repo, 'session'):
                self._audit_repo.session.commit()

            log_secure_info(
                "info",
                f"Result processed for job {result.job_id}, stage {result.stage_name}",
                result.request_id,
            )

        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Error handling result: job_id=%s, error=%s",
                result.job_id,
                exc,
            )

    # ------------------------------------------------------------------
    # S1-4 Part B: Build-image completion — ImageGroup/Image creation
    # ------------------------------------------------------------------

    @staticmethod
    def _is_build_image_stage(stage_name: str) -> bool:
        """Check if the stage is a build-image stage."""
        return stage_name in (
            "build-image-x86_64",
            "build-image-aarch64",
            "build-image",
        )

    def _on_build_image_success(self, result: PlaybookResult) -> None:
        """Create ImageGroup (BUILT) and Image records on build-image success.

        Loads catalog metadata persisted by parse-catalog, creates the
        ImageGroup with status BUILT, and inserts Image records for each
        constituent role.

        Args:
            result: Playbook execution result from NFS queue.
        """
        if self._image_group_repo is None or self._image_repo is None:
            logger.warning(
                "ImageGroup/Image repos not available; skipping "
                "ImageGroup creation for job=%s",
                result.job_id,
            )
            return

        try:
            catalog_metadata = self._load_catalog_metadata(result.job_id)
            if catalog_metadata is None:
                logger.warning(
                    "No catalog metadata found for job=%s; "
                    "skipping ImageGroup creation",
                    result.job_id,
                )
                return

            image_group_id = catalog_metadata["image_group_id"]
            role_images = catalog_metadata.get("role_images", {})

            # Create ImageGroup entity
            now = datetime.now(timezone.utc)
            image_group = ImageGroup(
                id=ImageGroupId(image_group_id),
                job_id=JobId(str(result.job_id)),
                status=ImageGroupStatus.BUILT,
                images=[],
                created_at=now,
                updated_at=now,
            )

            # Create Image entities for each role
            images = []
            for role_name, image_name in role_images.items():
                image = Image(
                    id=str(uuid.uuid4()),
                    image_group_id=image_group_id,
                    role=role_name,
                    image_name=image_name,
                    created_at=now,
                )
                images.append(image)
            image_group.images = images

            # Persist atomically
            try:
                self._image_group_repo.save(image_group)
                self._image_repo.save_batch(images)
            except IntegrityError:
                # Race condition: another completion already created this
                # ImageGroup (primary key collision). Log and skip.
                logger.warning(
                    "ImageGroup '%s' already exists (race condition). "
                    "Skipping duplicate creation for job=%s.",
                    image_group_id,
                    result.job_id,
                )
                if hasattr(self._image_group_repo, 'session'):
                    self._image_group_repo.session.rollback()
                return

            # Commit ImageGroup/Image records
            if hasattr(self._image_group_repo, 'session'):
                self._image_group_repo.session.commit()

            logger.info(
                "Build-image SUCCESS for job=%s. Created ImageGroup '%s' "
                "with %d images (status=BUILT).",
                result.job_id,
                image_group_id,
                len(images),
            )

        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Failed to create ImageGroup/Images for job=%s: %s",
                result.job_id,
                exc,
            )

    def _load_catalog_metadata(self, job_id) -> dict:
        """Load catalog metadata artifact persisted by parse-catalog.

        Retrieves the catalog-metadata artifact from the artifact store
        to get image_group_id and role-to-image mappings.

        Args:
            job_id: Job identifier.

        Returns:
            Dict with image_group_id, roles, role_images, or None if not found.
        """
        if self._artifact_metadata_repo is None or self._artifact_store is None:
            return None

        try:
            record = self._artifact_metadata_repo.find_by_job_stage_and_label(
                job_id=job_id,
                stage_name=StageName("parse-catalog"),
                label="catalog-metadata",
            )
            if record is None:
                return None

            raw = self._artifact_store.retrieve(
                record.artifact_ref.key,
                ArtifactKind.FILE,
            )
            return json.loads(raw.decode("utf-8"))

        except Exception as exc:  # pylint: disable=broad-except
            logger.warning(
                "Failed to load catalog metadata for job=%s: %s",
                job_id,
                exc,
            )
            return None
