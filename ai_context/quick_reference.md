# Quick Reference - AI Content Factory
**Generated**: 2025-06-02 20:54:42

## 🔗 API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | /healthz | Health check |
| GET | /users/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| PUT | /items/{item_id} | API endpoint |
| POST | /items/ | API endpoint |
| DELETE | /items/{item_id} | API endpoint |
| PATCH | /items/ | API endpoint |
| PUT | /items/{item_id} | API endpoint |
| POST | /send-notification/{email} | API endpoint |
| GET | /users/ | API endpoint |
| GET | /items/ | API endpoint |
| PUT | /items/{item_id} | API endpoint |
| POST | /items/ | API endpoint |
| DELETE | /items/{item_id} | API endpoint |
| PATCH | /items/ | API endpoint |
| GET | /items/{item_id} | API endpoint |
| GET | /items/{item_id} | API endpoint |
| GET | /items/ | API endpoint |
| GET | /users/me/items/ | API endpoint |
| POST | /files/ | API endpoint |
| POST | /uploadfile/ | API endpoint |
| POST | /login | API endpoint |
| POST | /login | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /users/me | API endpoint |
| GET | /users/me | API endpoint |
| GET | /users/me | API endpoint |
| GET | /users/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| PUT | /items/{item_id} | API endpoint |
| POST | /items/ | API endpoint |
| DELETE | /items/{item_id} | API endpoint |
| PATCH | /items/ | API endpoint |
| PUT | /items/{item_id} | API endpoint |
| POST | /send-notification/{email} | API endpoint |
| GET | /users/ | API endpoint |
| GET | /items/ | API endpoint |
| PUT | /items/{item_id} | API endpoint |
| POST | /items/ | API endpoint |
| DELETE | /items/{item_id} | API endpoint |
| PATCH | /items/ | API endpoint |
| GET | /items/{item_id} | API endpoint |
| GET | /items/{item_id} | API endpoint |
| GET | /items/ | API endpoint |
| GET | /users/me/items/ | API endpoint |
| POST | /files/ | API endpoint |
| POST | /uploadfile/ | API endpoint |
| POST | /login | API endpoint |
| POST | /login | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /items/ | API endpoint |
| GET | /users/me | API endpoint |
| GET | /users/me | API endpoint |
| GET | /users/me | API endpoint |
| POST | /process-generation-task | API endpoint |
| GET | /health | Health check |
| POST | /register | API endpoint |
| POST | /login | API endpoint |
| GET | /users/me | API endpoint |
| POST | /content/{content_id}/feedback | Content generation |
| GET | /content/{content_id}/feedback | Content generation |
| GET | /{job_id} | Job management |
| PATCH | /{job_id} | Job management |
| DELETE | /{job_id} | Job management |
| POST | /generate | API endpoint |

## 📋 Data Models

| Model | Purpose | File |
|-------|---------|------|
| BaseSettings | Base class for settings, allowing values to be overridden by environment variables. | venv/lib/python3.13/site-packages/pydantic_settings/main.py |
| RootModel | Usage docs: https://docs.pydantic.dev/2.8/concepts/models/#rootmodel-and-custom-root-types | venv/lib/python3.13/site-packages/pydantic/root_model.py |
| GenericModel | Data model | venv/lib/python3.13/site-packages/openai/_models.py |
| ModelDeleted | Data model | venv/lib/python3.13/site-packages/openai/types/model_deleted.py |
| Completion | Data model | venv/lib/python3.13/site-packages/openai/types/completion.py |
| Hyperparams | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tune.py |
| FineTune | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tune.py |
| Embedding | Data model | venv/lib/python3.13/site-packages/openai/types/embedding.py |
| Categories | Data model | venv/lib/python3.13/site-packages/openai/types/moderation.py |
| CategoryScores | Data model | venv/lib/python3.13/site-packages/openai/types/moderation.py |
| Moderation | Data model | venv/lib/python3.13/site-packages/openai/types/moderation.py |
| Choice | Data model | venv/lib/python3.13/site-packages/openai/types/edit.py |
| Edit | Data model | venv/lib/python3.13/site-packages/openai/types/edit.py |
| Logprobs | Data model | venv/lib/python3.13/site-packages/openai/types/completion_choice.py |
| CompletionChoice | Data model | venv/lib/python3.13/site-packages/openai/types/completion_choice.py |
| FineTuneEvent | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tune_event.py |
| Model | Data model | venv/lib/python3.13/site-packages/openai/types/model.py |
| FileDeleted | Data model | venv/lib/python3.13/site-packages/openai/types/file_deleted.py |
| Usage | Data model | venv/lib/python3.13/site-packages/openai/types/create_embedding_response.py |
| CreateEmbeddingResponse | Data model | venv/lib/python3.13/site-packages/openai/types/create_embedding_response.py |
| ImagesResponse | Data model | venv/lib/python3.13/site-packages/openai/types/images_response.py |
| CompletionUsage | Data model | venv/lib/python3.13/site-packages/openai/types/completion_usage.py |
| ModerationCreateResponse | Data model | venv/lib/python3.13/site-packages/openai/types/moderation_create_response.py |
| Image | Data model | venv/lib/python3.13/site-packages/openai/types/image.py |
| FileObject | Data model | venv/lib/python3.13/site-packages/openai/types/file_object.py |
| FineTuneEventsListResponse | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tune_events_list_response.py |
| Arguments | Data model | venv/lib/python3.13/site-packages/openai/cli/_cli.py |
| CLIFileIDArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/files.py |
| CLIFileCreateArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/files.py |
| CLIModelIDArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/models.py |
| CLICompletionCreateArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/completions.py |
| CLITranscribeArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/audio.py |
| CLITranslationArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/audio.py |
| CLIImageCreateArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/image.py |
| CLIImageCreateVariationArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/image.py |
| CLIImageEditArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/image.py |
| PrepareDataArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_tools/fine_tunes.py |
| GritArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_tools/migrate.py |
| MigrateArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_tools/migrate.py |
| CLIChatCompletionCreateArgs | Data model | venv/lib/python3.13/site-packages/openai/cli/_api/chat/completions.py |
| Thread | Data model | venv/lib/python3.13/site-packages/openai/types/beta/thread.py |
| ThreadDeleted | Data model | venv/lib/python3.13/site-packages/openai/types/beta/thread_deleted.py |
| ToolCodeInterpreter | Data model | venv/lib/python3.13/site-packages/openai/types/beta/assistant.py |
| ToolRetrieval | Data model | venv/lib/python3.13/site-packages/openai/types/beta/assistant.py |
| ToolFunction | Data model | venv/lib/python3.13/site-packages/openai/types/beta/assistant.py |
| Assistant | Data model | venv/lib/python3.13/site-packages/openai/types/beta/assistant.py |
| AssistantDeleted | Data model | venv/lib/python3.13/site-packages/openai/types/beta/assistant_deleted.py |
| Error | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tuning/fine_tuning_job.py |
| Hyperparameters | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tuning/fine_tuning_job.py |
| FineTuningJob | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tuning/fine_tuning_job.py |
| FineTuningJobEvent | Data model | venv/lib/python3.13/site-packages/openai/types/fine_tuning/fine_tuning_job_event.py |
| FunctionCall | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_message.py |
| ChatCompletionMessage | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_message.py |
| Choice | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion.py |
| ChatCompletion | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion.py |
| ChoiceDeltaFunctionCall | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_chunk.py |
| ChoiceDeltaToolCallFunction | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_chunk.py |
| ChoiceDeltaToolCall | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_chunk.py |
| ChoiceDelta | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_chunk.py |
| Choice | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_chunk.py |
| ChatCompletionChunk | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_chunk.py |
| Function | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_message_tool_call.py |
| ChatCompletionMessageToolCall | Data model | venv/lib/python3.13/site-packages/openai/types/chat/chat_completion_message_tool_call.py |
| FunctionDefinition | Data model | venv/lib/python3.13/site-packages/openai/types/shared/function_definition.py |
| Transcription | Data model | venv/lib/python3.13/site-packages/openai/types/audio/transcription.py |
| Translation | Data model | venv/lib/python3.13/site-packages/openai/types/audio/translation.py |
| FileDeleteResponse | Data model | venv/lib/python3.13/site-packages/openai/types/beta/assistants/file_delete_response.py |
| AssistantFile | Data model | venv/lib/python3.13/site-packages/openai/types/beta/assistants/assistant_file.py |
| LastError | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/run.py |
| RequiredActionSubmitToolOutputs | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/run.py |
| RequiredAction | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/run.py |
| ToolAssistantToolsCode | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/run.py |
| ToolAssistantToolsRetrieval | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/run.py |
| ToolAssistantToolsFunction | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/run.py |
| Run | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/run.py |
| TextAnnotationFileCitationFileCitation | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_text.py |
| TextAnnotationFileCitation | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_text.py |
| TextAnnotationFilePathFilePath | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_text.py |
| TextAnnotationFilePath | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_text.py |
| Text | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_text.py |
| MessageContentText | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_text.py |
| ImageFile | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_image_file.py |
| MessageContentImageFile | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/message_content_image_file.py |
| ThreadMessage | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/thread_message.py |
| Function | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/required_action_function_tool_call.py |
| RequiredActionFunctionToolCall | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/required_action_function_tool_call.py |
| MessageFile | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/messages/message_file.py |
| Function | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/function_tool_call.py |
| FunctionToolCall | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/function_tool_call.py |
| LastError | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/run_step.py |
| RunStep | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/run_step.py |
| CodeInterpreterOutputLogs | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/code_tool_call.py |
| CodeInterpreterOutputImageImage | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/code_tool_call.py |
| CodeInterpreterOutputImage | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/code_tool_call.py |
| CodeInterpreter | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/code_tool_call.py |
| CodeToolCall | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/code_tool_call.py |
| ToolCallsStepDetails | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/tool_calls_step_details.py |
| RetrievalToolCall | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/retrieval_tool_call.py |
| MessageCreation | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/message_creation_step_details.py |
| MessageCreationStepDetails | Data model | venv/lib/python3.13/site-packages/openai/types/beta/threads/runs/message_creation_step_details.py |
| DecoratorBaseModel | Data model | venv/lib/python3.13/site-packages/pydantic/v1/decorator.py |
| BaseSettings | Base class for settings, allowing values to be overridden by environment variables. | venv/lib/python3.13/site-packages/pydantic/v1/env_settings.py |
| GenericModel | Data model | venv/lib/python3.13/site-packages/pydantic/v1/generics.py |
| DecoratorBaseModel | Data model | venv/lib/python3.13/site-packages/pydantic/deprecated/decorator.py |
| HTTPBasicCredentials | The HTTP Basic credentials given as the result of using `HTTPBasic` in a | venv/lib/python3.13/site-packages/fastapi/security/http.py |
| HTTPAuthorizationCredentials | The HTTP authorization credentials in the result of using `HTTPBearer` or | venv/lib/python3.13/site-packages/fastapi/security/http.py |
| BaseModelWithConfig | Data model | venv/lib/python3.13/site-packages/fastapi/openapi/models.py |
| Reference | Data model | venv/lib/python3.13/site-packages/fastapi/openapi/models.py |
| Discriminator | Data model | venv/lib/python3.13/site-packages/fastapi/openapi/models.py |
| SchemaModelV30 | Data model | venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py |
| Remediation | Data model | venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py |
| SpecificationVulnerabilities | Data model | venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py |
| AnalyzedSpecification | Data model | venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py |
| Package | Data model | venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py |
| Results | Data model | venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py |
| ScanResults | Data model | venv/lib/python3.13/site-packages/safety_schemas/report/schemas/v3_0/main.py |
| EventBatchApiPayload | A batch of events for the /events API endpoint. | venv/lib/python3.13/site-packages/safety_schemas/models/api/events.py |
| ClientInfo | Information about the client application. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| ProjectInfo | Information about the project context. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| UserInfo | Information about the user. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| OsInfo | Information about the operating system. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| HostInfo | Information about the host machine. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| PythonInfo | Detailed information about the Python environment. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| RuntimeInfo | Information about the runtime environment. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| EventContext | Complete context information for an event. | venv/lib/python3.13/site-packages/safety_schemas/models/events/context.py |
| PayloadBase | Base class for all event payloads | venv/lib/python3.13/site-packages/safety_schemas/models/events/base.py |
| Event | Data model | venv/lib/python3.13/site-packages/safety_schemas/models/events/base.py |
| DependencyFile | Information about a detected dependency file. | venv/lib/python3.13/site-packages/safety_schemas/models/events/payloads/onboarding.py |
| CommandParam | Data model | venv/lib/python3.13/site-packages/safety_schemas/models/events/payloads/main.py |
| ProcessStatus | Data model | venv/lib/python3.13/site-packages/safety_schemas/models/events/payloads/main.py |
| HealthCheckResult | Generic health check result structure. | venv/lib/python3.13/site-packages/safety_schemas/models/events/payloads/main.py |
| IndexConfig | Configuration details for the package index. | venv/lib/python3.13/site-packages/safety_schemas/models/events/payloads/main.py |
| AliasConfig | Configuration details for the command alias. | venv/lib/python3.13/site-packages/safety_schemas/models/events/payloads/main.py |
| ToolStatus | Status of a single package manager tool. A single package manager tool is | venv/lib/python3.13/site-packages/safety_schemas/models/events/payloads/main.py |
| SchemaModelV30 | Data model | venv/lib/python3.13/site-packages/safety_schemas/config/schemas/v3_0/main.py |
| BaseScanResult | Base class for all scan results with common attributes | venv/lib/python3.13/site-packages/safety/scan/init_scan.py |
| ContextSettingsModel | Model for command context settings. | venv/lib/python3.13/site-packages/safety/tool/definitions.py |
| CommandSettingsModel | Model for command settings used in the Typer decorator. | venv/lib/python3.13/site-packages/safety/tool/definitions.py |
| ToolCommandModel | Model for a tool command definition. | venv/lib/python3.13/site-packages/safety/tool/definitions.py |
| Meta | Metadata for the scan report. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| Package | Information about a package and its vulnerabilities. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| OSVulnerabilities | Information about OS vulnerabilities. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| EnvironmentFindings | Findings related to the environment. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| Environment | Details about the environment being scanned. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| DependencyVulnerabilities | Information about dependency vulnerabilities. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| FileFindings | Findings related to a file. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| Remediations | Remediations for vulnerabilities. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| File | Information about a scanned file. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| Results | The results of a scan. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| ScanReportV30 | The scan report. | venv/lib/python3.13/site-packages/safety/formatters/schemas/v3_0.py |
| API | Data model | venv/lib/python3.13/site-packages/elevenlabs/api/base.py |
| BaseSettings | Base class for settings, allowing values to be overridden by environment variables. | .venv/lib/python3.13/site-packages/pydantic_settings/main.py |
| RootModel | !!! abstract "Usage Documentation" | .venv/lib/python3.13/site-packages/pydantic/root_model.py |
| DecoratorBaseModel | Data model | .venv/lib/python3.13/site-packages/pydantic/v1/decorator.py |
| BaseSettings | Base class for settings, allowing values to be overridden by environment variables. | .venv/lib/python3.13/site-packages/pydantic/v1/env_settings.py |
| GenericModel | Data model | .venv/lib/python3.13/site-packages/pydantic/v1/generics.py |
| DecoratorBaseModel | Data model | .venv/lib/python3.13/site-packages/pydantic/deprecated/decorator.py |
| CliMutuallyExclusiveGroup | Data model | .venv/lib/python3.13/site-packages/pydantic_settings/sources/providers/cli.py |
| HTTPBasicCredentials | The HTTP Basic credentials given as the result of using `HTTPBasic` in a | .venv/lib/python3.13/site-packages/fastapi/security/http.py |
| HTTPAuthorizationCredentials | The HTTP authorization credentials in the result of using `HTTPBearer` or | .venv/lib/python3.13/site-packages/fastapi/security/http.py |
| BaseModelWithConfig | Data model | .venv/lib/python3.13/site-packages/fastapi/openapi/models.py |
| Reference | Data model | .venv/lib/python3.13/site-packages/fastapi/openapi/models.py |
| Discriminator | Data model | .venv/lib/python3.13/site-packages/fastapi/openapi/models.py |
| TaskPayload | Model for Cloud Tasks payload. | app/api/routes/worker.py |
| WorkerResponse | Model for worker response. | app/api/routes/worker.py |
| Token | Response model for the token. | app/api/routes/auth.py |
| UserBase | Base model for user properties. | app/models/pydantic/user.py |
| TokenData | Data model | app/models/pydantic/user.py |
| UserResponse | Model for returning user data in API responses (excludes sensitive fields). | app/models/pydantic/user.py |
| FeedbackBase | Base model for feedback. | app/models/pydantic/feedback.py |
| JobError | Model for job error information. | app/models/pydantic/job.py |
| JobProgress | Model for tracking job progress. | app/models/pydantic/job.py |
| Job | Model for a content generation job. | app/models/pydantic/job.py |
| JobCreate | Model for creating a new job. | app/models/pydantic/job.py |
| JobUpdate | Model for updating an existing job. | app/models/pydantic/job.py |
| JobList | Model for listing jobs. | app/models/pydantic/job.py |
| ContentRequest | Request model for generating content. | app/models/pydantic/content.py |
| ContentMetadata | Metadata associated with the generated content. | app/models/pydantic/content.py |
| QualityMetrics | Quality metrics for the generated content. | app/models/pydantic/content.py |
| OutlineSection | Individual section within a content outline. | app/models/pydantic/content.py |
| ContentOutline | Structured content outline - the foundation for all other content. | app/models/pydantic/content.py |
| PodcastScript | Podcast script with structured content. | app/models/pydantic/content.py |
| StudyGuide | Comprehensive study guide. | app/models/pydantic/content.py |
| OnePagerSummary | Concise one-page summary. | app/models/pydantic/content.py |
| DetailedReadingMaterial | Comprehensive reading material. | app/models/pydantic/content.py |
| FAQItem | Individual FAQ item. | app/models/pydantic/content.py |
| FAQCollection | Collection of FAQ items. | app/models/pydantic/content.py |
| FlashcardItem | Individual flashcard. | app/models/pydantic/content.py |
| FlashcardCollection | Collection of flashcards. | app/models/pydantic/content.py |
| ReadingGuideQuestions | Reading guide questions. | app/models/pydantic/content.py |
| GeneratedContent | Complete generated content with all components. | app/models/pydantic/content.py |
| ContentResponse | Complete response for content generation. | app/models/pydantic/content.py |
| ErrorDetail | Data model | app/models/pydantic/content.py |
| HTTPValidationError | Data model | app/models/pydantic/content.py |
| APIErrorResponse | Standard error response model. | app/models/pydantic/content.py |

## 🛠 Common Debug Commands

```bash
# Start local development
./scripts/run_local.sh

# Check API health
curl http://localhost:8000/health

# Test job creation
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{"syllabus_text": "Test topic"}'

# Build Docker image
docker build -t ai-content-factory .

# Run with Docker
docker run -p 8000:8000 ai-content-factory
```

## 🔍 Log Locations

- **Application logs**: stdout/stderr in Docker container
- **Cloud Run logs**: GCP Console → Cloud Run → Service → Logs
- **Local development**: Terminal output

## ⚡ Quick Fixes

**Database Connection Issues:**
1. Check `GOOGLE_CLOUD_PROJECT` environment variable
2. Run `gcloud auth application-default login`
3. Verify Firestore API is enabled

**Import Errors:**
1. Check virtual environment is activated
2. Run `pip install -r requirements.txt`
3. Verify Python 3.11+ is being used

**Docker Build Failures:**
1. Check Dockerfile syntax
2. Verify all requirements.txt dependencies exist
3. Clear Docker cache: `docker system prune`
