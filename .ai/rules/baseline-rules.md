Baseline rules for AI-assisted software development:

1. All interactions between the human and agent must be documented in .ai\audit\chat.md. To save context, simply append the most recent back-and-forth to the end of the document, followed by two carriage returns. Do not read the file unless it is necessary to understand previous requests.

2. Do not make any changes to code without receiving permission from the user first.

3. During planning phases, all requirements must be clear, unambiguous, and free from contradictions. If such ambiguities or contradictions exist, ask the user clarifying questions to remove these concerns before proceeding. Write your questions to a file in the .ai\plans directory using the format specified in .ai\rules\question-format-guide.md. The human will update your generated file with his answers and inform you when he is done. Repeat the process, if necessary, until these issues are cleared up.

**Critical:** Do not ask questions in the chat window. Write a file in the .ai\plans folder using the question-format-guide.md format.

**Critical:** Do not proceed to later steps without clearing up ambiguities or contradictions.

4. Work with the human to create and update the .ai\plans\execution-plan.md document as the project progresses.
