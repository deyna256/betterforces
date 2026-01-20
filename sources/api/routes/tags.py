"""Tags API routes."""

from litestar import get
from litestar.params import Parameter
from litestar.response import Response

from sources.api.deps import codeforces_data_service_dependency, tags_service_dependency
from sources.api.routes.base import BaseMetricController
from sources.api.schemas.tags import SimpleTagInfoSchema, TagsResponse, WeakTagsResponse
from sources.domain.services.tags_service import TagsService
from sources.services.codeforces_data_service import CodeforcesDataService


class TagsController(BaseMetricController):
    """Controller for tags endpoints."""

    path = "/tags"
    tags = ["Tags"]

    @get(
        path="/{handle:str}",
        dependencies={
            "data_service": codeforces_data_service_dependency,
            "tags_service": tags_service_dependency,
        },
    )
    async def get_tags(
        self, handle: str, data_service: CodeforcesDataService, tags_service: TagsService
    ) -> Response[TagsResponse]:
        """
        Get user's solved problems analyzed by tags.

        Returns statistics showing average rating for each tag and problem count.

        Args:
            handle: Codeforces handle

        Returns:
            Tags analysis with average ratings by tag
        """
        submissions = await data_service.get_user_submissions(handle)

        self._validate_submissions_exist(submissions, handle)

        tags_analysis = tags_service.analyze_tags(handle, submissions)

        tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in tags_analysis.tags]

        response = TagsResponse(
            tags=tags_info,
            overall_average_rating=tags_analysis.overall_average_rating,
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
    async def get_weak_tags(
        self,
        handle: str,
        data_service: CodeforcesDataService,
        tags_service: TagsService,
        threshold: int = Parameter(
            default=200,
            ge=0,
            le=1000,
            description="Minimum rating difference to consider a tag 'weak'",
        ),
    ) -> Response[WeakTagsResponse]:
        """
        Get user's weak tags - topics where average rating is significantly lower.

        Returns tags that may need more practice based on rating threshold.

        Args:
            handle: Codeforces handle
            threshold: Minimum rating difference from overall average to be considered weak

        Returns:
            Weak tags analysis
        """
        submissions = await data_service.get_user_submissions(handle)

        self._validate_submissions_exist(submissions, handle)

        tags_analysis = tags_service.analyze_tags(handle, submissions)

        weak_tags = tags_analysis.get_weak_tags(threshold)

        weak_tags_info = [SimpleTagInfoSchema.model_validate(tag) for tag in weak_tags]

        response = WeakTagsResponse(
            weak_tags=weak_tags_info,
            overall_average_rating=tags_analysis.overall_average_rating,
            total_solved=tags_analysis.total_solved,
            threshold_used=threshold,
            last_updated=self.get_current_timestamp(),
        )

        return Response(response, headers=self.CACHE_HEADERS)
