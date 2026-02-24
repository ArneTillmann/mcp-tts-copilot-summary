Only call the MCP speech tool when either threshold is exceeded:

- More than 4 response paragraphs, or
- More than 100 new code lines.

Use the summary already present in the model response as `summary_text`.
Do not create a second summarization pipeline.

Preferred tool: `speak_existing_summary`.
Fallback tool: `speak_text`.

When invoking, pass available metadata:

- `paragraph_count`
- `new_code_lines`
