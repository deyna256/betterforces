"""Tags API routes."""

from litestar import get
from litestar.params import Parameter
from litestar.response import Response
from litestar.exceptions import HTTPException

from backend.api.deps import codeforces_data_service_dependency, tags_service_dependency
from backend.api.routes.base import BaseMetricController
from backend.api.schemas.tags import SimpleTagInfoSchema, TagsResponse, WeakTagsResponse
from backend.domain.services.tags_service import TagsService
from backend.services.codeforces_data_service import CodeforcesDataService
from backend.infrastructure.codeforces_client import UserNotFoundError


class TagsController(BaseMetricController):
    """Controller for tag ratings endpoints."""

    path = "/tag-ratings"
    tags = ["Tag Ratings"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "tags_service": tags_service_dependency,
        },
    )
    async def get_tag_ratings(
        self, handle: str, data_service: CodeforcesDataService, tags_service: TagsService
    ) -> Response[TagsResponse]:
        """
        Get user's average and median rating by problem tags.

        Returns performance analysis showing median and average rating for each tag,
        helping identify strengths and weaknesses in different topics.

        Args:
            handle: Codeforces handle

        Returns:
            Tag ratings with median and average ratings by tag
        """
        try:
            submissions = await data_service.get_user_submissions(handle)
        except UserNotFoundError:
            raise HTTPException(
                status_code=404,
                detail=f"User '{handle}' not found on Codeforces"
            )

        self._validate_submissions_exist(submissions, handle)

        tags_analysis = tags_service.analyze_tags(handle, submissions)

        tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in tags_analysis.tags]

        response = TagsResponse(
            tags=tags_info,
            overall_average_rating=tags_analysis.overall_average_rating,
            overall_median_rating=tags_analysis.overall_median_rating,
            total_solved=tags_analysis.total_solved,
            last_updated=self.get_current_timestamp(),
        )

        return Response(response, headers=self.CACHE_HEADERS)

    @get(
        path="/{handle:str}/weak",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "tags_service": tags_service_dependency,
        },
    )
    async def get_weak_tag_ratings(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        tags_service: TagsService,
        threshold: int = Parameter(
            default=200,
            ge=0,
            le=1000,
            description="Minimum rating difference to consider a tag rating 'weak'",
        ),
    ) -> Response[WeakTagsResponse]:
        """
        Get user's weak tag ratings - topics where median rating is significantly lower.

        Returns tags that may need more practice based on rating threshold from overall median.

        Args:
            handle: Codeforces handle
            threshold: Minimum rating difference from overall median to be considered weak

        Returns:
            Weak tag ratings analysis
        """
        submissions = await data_service.get_user_submissions(handle)

        self._validate_submissions_exist(submissions, handle)

        tags_analysis = tags_service.analyze_tags(handle, submissions)

        weak_tags = tags_analysis.get_weak_tags(threshold)

        weak_tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in weak_tags]

        response = WeakTagsResponse(
            weak_tags=weak_tags_info,
            overall_average_rating=tags_analysis.overall_average_rating,
            overall_median_rating=tags_analysis.overall_median_rating,
            total_solved=tags_analysis.total_solved,
            threshold_used=threshold,
            last_updated=self.get_current_timestamp(),
        )

        return Response(response, headers=self.CACHE_HEADERS)
