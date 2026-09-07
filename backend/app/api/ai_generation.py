from fastapi import APIRouter, Depends, HTTPException, status

from app.ai.base import AIService, AIServiceError
from app.api.deps import (
    get_ai_interaction_repository,
    get_ai_service,
    get_current_user,
    get_mini_story_repository,
    get_profile_repository,
    get_question_repository,
    get_skill_repository,
)
from app.repositories.ai_interaction_repository import AIInteractionRepository
from app.repositories.mini_story_repository import MiniStoryRepository
from app.repositories.profile_repository import LearnerProfileRepository
from app.repositories.question_repository import QuestionRepository
from app.repositories.skill_repository import LearnerSkillRepository
from app.schemas.ai_generation import (
    GeneratedQuestionPublic,
    GenerateMiniStoryRequest,
    GenerateQuestionRequest,
    MiniStoryPublic,
    SubmitComprehensionRequest,
    SubmitComprehensionResponse,
    SubmitGeneratedQuestionRequest,
    SubmitGeneratedQuestionResponse,
    mini_story_to_public,
    question_to_public,
)
from app.services.content_generation_service import (
    ContentGenerationService,
    ProfileRequiredError,
    QuestionNotFoundError,
    StoryNotFoundError,
)

router = APIRouter()


def _service(
    ai: AIService = Depends(get_ai_service),
    questions: QuestionRepository = Depends(get_question_repository),
    stories: MiniStoryRepository = Depends(get_mini_story_repository),
    interactions: AIInteractionRepository = Depends(get_ai_interaction_repository),
    profiles: LearnerProfileRepository = Depends(get_profile_repository),
    skills: LearnerSkillRepository = Depends(get_skill_repository),
) -> ContentGenerationService:
    return ContentGenerationService(ai, questions, stories, interactions, profiles, skills)


def _generation_failed() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="The AI tutor couldn't generate that content. Please try again.",
    )


@router.post("/generate/vocabulary-question", response_model=GeneratedQuestionPublic)
async def generate_vocabulary_question(
    payload: GenerateQuestionRequest,
    current_user: dict = Depends(get_current_user),
    service: ContentGenerationService = Depends(_service),
) -> GeneratedQuestionPublic:
    try:
        doc = await service.generate_vocabulary_question(
            str(current_user["_id"]), payload.level.value
        )
    except AIServiceError as exc:
        raise _generation_failed() from exc
    return question_to_public(doc)


@router.post("/generate/grammar-question", response_model=GeneratedQuestionPublic)
async def generate_grammar_question(
    payload: GenerateQuestionRequest,
    current_user: dict = Depends(get_current_user),
    service: ContentGenerationService = Depends(_service),
) -> GeneratedQuestionPublic:
    try:
        doc = await service.generate_grammar_question(str(current_user["_id"]), payload.level.value)
    except AIServiceError as exc:
        raise _generation_failed() from exc
    return question_to_public(doc)


@router.post("/generate/mini-story", response_model=MiniStoryPublic)
async def generate_mini_story(
    payload: GenerateMiniStoryRequest,
    current_user: dict = Depends(get_current_user),
    service: ContentGenerationService = Depends(_service),
) -> MiniStoryPublic:
    try:
        doc = await service.generate_mini_story(
            str(current_user["_id"]), payload.level.value, payload.topic
        )
    except AIServiceError as exc:
        raise _generation_failed() from exc
    return mini_story_to_public(doc)


@router.post(
    "/mini-stories/{story_id}/comprehension/submit",
    response_model=SubmitComprehensionResponse,
)
async def submit_comprehension(
    story_id: str,
    payload: SubmitComprehensionRequest,
    current_user: dict = Depends(get_current_user),
    service: ContentGenerationService = Depends(_service),
) -> SubmitComprehensionResponse:
    try:
        result = await service.submit_comprehension(
            str(current_user["_id"]), story_id, payload.answers
        )
    except ProfileRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        ) from exc
    except StoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Story not found"
        ) from exc
    return SubmitComprehensionResponse(**result)


@router.post(
    "/generated-questions/{question_id}/submit",
    response_model=SubmitGeneratedQuestionResponse,
)
async def submit_generated_question(
    question_id: str,
    payload: SubmitGeneratedQuestionRequest,
    current_user: dict = Depends(get_current_user),
    service: ContentGenerationService = Depends(_service),
) -> SubmitGeneratedQuestionResponse:
    try:
        result = await service.submit_generated_question(
            str(current_user["_id"]), question_id, payload.selected
        )
    except ProfileRequiredError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Onboarding not completed yet"
        ) from exc
    except QuestionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Question not found"
        ) from exc
    return SubmitGeneratedQuestionResponse(**result)
