Messages
Messages

Copy page

Send a structured list of input messages with text and/or image content, and the model will generate the next message in the conversation.

The Messages API can be used for either single queries or stateless multi-turn conversations.

Learn more about the Messages API in our user guide

POST
/
v1
/
messages
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Body
application/json
​
model
stringrequired
The model that will complete your prompt.

See models for additional details and options.

Required string length: 1 - 256
Examples:
"claude-3-7-sonnet-20250219"
​
messages
object[]required
Input messages.

Our models are trained to operate on alternating user and assistant conversational turns. When creating a new Message, you specify the prior conversational turns with the messages parameter, and the model then generates the next Message in the conversation. Consecutive user or assistant turns in your request will be combined into a single turn.

Each input message must be an object with a role and content. You can specify a single user-role message, or you can include multiple user and assistant messages.

If the final message uses the assistant role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

Example with a single user message:

[{"role": "user", "content": "Hello, Claude"}]
Example with multiple conversational turns:

[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"},
]
Example with a partially-filled response from Claude:

[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("},
]
Each input message content may be either a single string or an array of content blocks, where each block has a specific type. Using a string for content is shorthand for an array of one content block of type "text". The following input messages are equivalent:

{"role": "user", "content": "Hello, Claude"}
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}
Starting with Claude 3 models, you can also send image content blocks:

{"role": "user", "content": [
  {
    "type": "image",
    "source": {
      "type": "base64",
      "media_type": "image/jpeg",
      "data": "/9j/4AAQSkZJRg...",
    }
  },
  {"type": "text", "text": "What is in this image?"}
]}
We currently support the base64 source type for images, and the image/jpeg, image/png, image/gif, and image/webp media types.

See examples for more input examples.

Note that if you want to include a system prompt, you can use the top-level system parameter — there is no "system" role for input messages in the Messages API.

There is a limit of 100,000 messages in a single request.


Show child attributes

​
max_tokens
integerrequired
The maximum number of tokens to generate before stopping.

Note that our models may stop before reaching this maximum. This parameter only specifies the absolute maximum number of tokens to generate.

Different models have different maximum values for this parameter. See models for details.

Required range: x >= 1
Examples:
1024
​
container
string | null
Container identifier for reuse across requests.

​
mcp_servers
object[]
MCP servers to be utilized in this request


Show child attributes

​
metadata
object
An object describing metadata about the request.


Show child attributes

​
service_tier
enum<string>
Determines whether to use priority capacity (if available) or standard capacity for this request.

Anthropic offers different levels of service for your API requests. See service-tiers for details.

Available options: auto, standard_only 
​
stop_sequences
string[]
Custom text sequences that will cause the model to stop generating.

Our models will normally stop when they have naturally completed their turn, which will result in a response stop_reason of "end_turn".

If you want the model to stop generating when it encounters custom strings of text, you can use the stop_sequences parameter. If the model encounters one of the custom sequences, the response stop_reason value will be "stop_sequence" and the response stop_sequence value will contain the matched stop sequence.

​
stream
boolean
Whether to incrementally stream the response using server-sent events.

See streaming for details.

​
system

string
System prompt.

A system prompt is a way of providing context and instructions to Claude, such as specifying a particular goal or role. See our guide to system prompts.

Examples:
[
  {
    "text": "Today's date is 2024-06-01.",
    "type": "text"
  }
]
"Today's date is 2023-01-01."

​
temperature
number
Amount of randomness injected into the response.

Defaults to 1.0. Ranges from 0.0 to 1.0. Use temperature closer to 0.0 for analytical / multiple choice, and closer to 1.0 for creative and generative tasks.

Note that even with temperature of 0.0, the results will not be fully deterministic.

Required range: 0 <= x <= 1
Examples:
1
​
thinking
object
Configuration for enabling Claude's extended thinking.

When enabled, responses include thinking content blocks showing Claude's thinking process before the final answer. Requires a minimum budget of 1,024 tokens and counts towards your max_tokens limit.

See extended thinking for details.

Enabled
Disabled

Show child attributes

​
tool_choice
object
How the model should use the provided tools. The model can use a specific tool, any available tool, decide by itself, or not use tools at all.

Auto
Any
Tool
None

Show child attributes

​
tools
object[]
Definitions of tools that the model may use.

If you include tools in your API request, the model may return tool_use content blocks that represent the model's use of those tools. You can then run those tools using the tool input generated by the model and then optionally return results back to the model using tool_result content blocks.

Each tool definition includes:

name: Name of the tool.
description: Optional, but strongly-recommended description of the tool.
input_schema: JSON schema for the tool input shape that the model will produce in tool_use output content blocks.
For example, if you defined tools as:

[
  {
    "name": "get_stock_price",
    "description": "Get the current stock price for a given ticker symbol.",
    "input_schema": {
      "type": "object",
      "properties": {
        "ticker": {
          "type": "string",
          "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
        }
      },
      "required": ["ticker"]
    }
  }
]
And then asked the model "What's the S&P 500 at today?", the model might produce tool_use content blocks in the response like this:

[
  {
    "type": "tool_use",
    "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "name": "get_stock_price",
    "input": { "ticker": "^GSPC" }
  }
]
You might then run your get_stock_price tool with {"ticker": "^GSPC"} as an input, and return the following back to the model in a subsequent user message:

[
  {
    "type": "tool_result",
    "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "content": "259.75 USD"
  }
]
Tools can be used for workflows that include running client-side tools and functions, or more generally whenever you want the model to produce a particular JSON structure of output.

See our guide for more details.

Custom tool
Computer use tool (2024-01-22)
Bash tool (2024-10-22)
Text editor tool (2024-10-22)
Computer use tool (2025-01-24)
Bash tool (2025-01-24)
Text editor tool (2025-01-24)
TextEditor_20250429
Web search tool (2025-03-05)
Code execution tool (2025-05-22)

Show child attributes

Examples:
{
  "description": "Get the current weather in a given location",
  "input_schema": {
    "properties": {
      "location": {
        "description": "The city and state, e.g. San Francisco, CA",
        "type": "string"
      },
      "unit": {
        "description": "Unit for the output - one of (celsius, fahrenheit)",
        "type": "string"
      }
    },
    "required": ["location"],
    "type": "object"
  },
  "name": "get_weather"
}
​
top_k
integer
Only sample from the top K options for each subsequent token.

Used to remove "long tail" low probability responses. Learn more technical details here.

Recommended for advanced use cases only. You usually only need to use temperature.

Required range: x >= 0
Examples:
5
​
top_p
number
Use nucleus sampling.

In nucleus sampling, we compute the cumulative distribution over all the options for each subsequent token in decreasing probability order and cut it off once it reaches a particular probability specified by top_p. You should either alter temperature or top_p, but not both.

Recommended for advanced use cases only. You usually only need to use temperature.

Required range: 0 <= x <= 1
Examples:
0.7
Response
200

200
application/json
Message object.
​
id
stringrequired
Unique object identifier.

The format and length of IDs may change over time.

Examples:
"msg_013Zva2CMHLNnXjNJJKqJ2EF"
​
type
enum<string>default:messagerequired
Object type.

For Messages, this is always "message".

Available options: message 
​
role
enum<string>default:assistantrequired
Conversational role of the generated message.

This will always be "assistant".

Available options: assistant 
​
content
object[]required
Content generated by the model.

This is an array of content blocks, each of which has a type that determines its shape.

Example:

[{"type": "text", "text": "Hi, I'm Claude."}]
If the request input messages ended with an assistant turn, then the response content will continue directly from that last turn. You can use this to constrain the model's output.

For example, if the input messages were:

[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("}
]
Then the response content might be:

[{"type": "text", "text": "B)"}]
Tool use
ResponseServerToolUseBlock
ResponseWebSearchToolResultBlock
ResponseCodeExecutionToolResultBlock
ResponseMCPToolUseBlock
ResponseMCPToolResultBlock
ResponseContainerUploadBlock
Thinking
Redacted thinking

Show child attributes

Examples:
[
  {
    "text": "Hi! My name is Claude.",
    "type": "text"
  }
]
​
model
stringrequired
The model that handled the request.

Required string length: 1 - 256
Examples:
"claude-3-7-sonnet-20250219"
​
stop_reason
enum<string> | nullrequired
The reason that we stopped.

This may be one the following values:

"end_turn": the model reached a natural stopping point
"max_tokens": we exceeded the requested max_tokens or the model's maximum
"stop_sequence": one of your provided custom stop_sequences was generated
"tool_use": the model invoked one or more tools
In non-streaming mode this value is always non-null. In streaming mode, it is null in the message_start event and non-null otherwise.

Available options: end_turn, max_tokens, stop_sequence, tool_use, pause_turn, refusal 
​
stop_sequence
string | nullrequired
Which custom stop sequence was generated, if any.

This value will be a non-null string if one of your custom stop sequences was generated.

​
usage
objectrequired
Billing and rate-limit usage.

Anthropic's API bills and rate-limits by token counts, as tokens represent the underlying cost to our systems.

Under the hood, the API transforms requests into a format suitable for the model. The model's output then goes through a parsing stage before becoming an API response. As a result, the token counts in usage will not match one-to-one with the exact visible content of an API request or response.

For example, output_tokens will be non-zero, even for an empty string response from Claude.

Total input tokens in a request is the summation of input_tokens, cache_creation_input_tokens, and cache_read_input_tokens.


Show child attributes

Examples:
{
  "input_tokens": 2095,
  "output_tokens": 503
}
​
container
object | nullrequired
Information about the container used in this request.

This will be non-null if a container tool (e.g. code execution) was used.


Show child attributes

Was this page helpful?


Yes

No
Handling stop reasons
Count Message tokens
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-7-sonnet-20250219",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Hello, world"}
    ]
}'

200

4XX

Copy
{
  "content": [
    {
      "text": "Hi! My name is Claude.",
      "type": "text"
    }
  ],
  "id": "msg_013Zva2CMHLNnXjNJJKqJ2EF",
  "model": "claude-3-7-sonnet-20250219",
  "role": "assistant",
  "stop_reason": "end_turn",
  "stop_sequence": null,
  "type": "message",
  "usage": {




    Messages
Count Message tokens

Copy page

Count the number of tokens in a Message.

The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

Learn more about token counting in our user guide

POST
/
v1
/
messages
/
count_tokens
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Body
application/json
​
messages
object[]required
Input messages.

Our models are trained to operate on alternating user and assistant conversational turns. When creating a new Message, you specify the prior conversational turns with the messages parameter, and the model then generates the next Message in the conversation. Consecutive user or assistant turns in your request will be combined into a single turn.

Each input message must be an object with a role and content. You can specify a single user-role message, or you can include multiple user and assistant messages.

If the final message uses the assistant role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

Example with a single user message:

[{"role": "user", "content": "Hello, Claude"}]
Example with multiple conversational turns:

[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"},
]
Example with a partially-filled response from Claude:

[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("},
]
Each input message content may be either a single string or an array of content blocks, where each block has a specific type. Using a string for content is shorthand for an array of one content block of type "text". The following input messages are equivalent:

{"role": "user", "content": "Hello, Claude"}
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}
Starting with Claude 3 models, you can also send image content blocks:

{"role": "user", "content": [
  {
    "type": "image",
    "source": {
      "type": "base64",
      "media_type": "image/jpeg",
      "data": "/9j/4AAQSkZJRg...",
    }
  },
  {"type": "text", "text": "What is in this image?"}
]}
We currently support the base64 source type for images, and the image/jpeg, image/png, image/gif, and image/webp media types.

See examples for more input examples.

Note that if you want to include a system prompt, you can use the top-level system parameter — there is no "system" role for input messages in the Messages API.

There is a limit of 100,000 messages in a single request.


Show child attributes

​
model
stringrequired
The model that will complete your prompt.

See models for additional details and options.

Required string length: 1 - 256
Examples:
"claude-3-7-sonnet-20250219"
​
mcp_servers
object[]
MCP servers to be utilized in this request


Show child attributes

​
system

string
System prompt.

A system prompt is a way of providing context and instructions to Claude, such as specifying a particular goal or role. See our guide to system prompts.

Examples:
[
  {
    "text": "Today's date is 2024-06-01.",
    "type": "text"
  }
]
"Today's date is 2023-01-01."

​
thinking
object
Configuration for enabling Claude's extended thinking.

When enabled, responses include thinking content blocks showing Claude's thinking process before the final answer. Requires a minimum budget of 1,024 tokens and counts towards your max_tokens limit.

See extended thinking for details.

Enabled
Disabled

Show child attributes

​
tool_choice
object
How the model should use the provided tools. The model can use a specific tool, any available tool, decide by itself, or not use tools at all.

Auto
Any
Tool
None

Show child attributes

​
tools
object[]
Definitions of tools that the model may use.

If you include tools in your API request, the model may return tool_use content blocks that represent the model's use of those tools. You can then run those tools using the tool input generated by the model and then optionally return results back to the model using tool_result content blocks.

Each tool definition includes:

name: Name of the tool.
description: Optional, but strongly-recommended description of the tool.
input_schema: JSON schema for the tool input shape that the model will produce in tool_use output content blocks.
For example, if you defined tools as:

[
  {
    "name": "get_stock_price",
    "description": "Get the current stock price for a given ticker symbol.",
    "input_schema": {
      "type": "object",
      "properties": {
        "ticker": {
          "type": "string",
          "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
        }
      },
      "required": ["ticker"]
    }
  }
]
And then asked the model "What's the S&P 500 at today?", the model might produce tool_use content blocks in the response like this:

[
  {
    "type": "tool_use",
    "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "name": "get_stock_price",
    "input": { "ticker": "^GSPC" }
  }
]
You might then run your get_stock_price tool with {"ticker": "^GSPC"} as an input, and return the following back to the model in a subsequent user message:

[
  {
    "type": "tool_result",
    "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "content": "259.75 USD"
  }
]
Tools can be used for workflows that include running client-side tools and functions, or more generally whenever you want the model to produce a particular JSON structure of output.

See our guide for more details.

Custom tool
Computer use tool (2024-01-22)
Bash tool (2024-10-22)
Text editor tool (2024-10-22)
Computer use tool (2025-01-24)
Bash tool (2025-01-24)
Text editor tool (2025-01-24)
TextEditor_20250429
Web search tool (2025-03-05)
Code execution tool (2025-05-22)

Show child attributes

Examples:
{
  "description": "Get the current weather in a given location",
  "input_schema": {
    "properties": {
      "location": {
        "description": "The city and state, e.g. San Francisco, CA",
        "type": "string"
      },
      "unit": {
        "description": "Unit for the output - one of (celsius, fahrenheit)",
        "type": "string"
      }
    },
    "required": ["location"],
    "type": "object"
  },
  "name": "get_weather"
}
Response
200

200
application/json
Successful Response
​
input_tokens
integerrequired
The total number of tokens across the provided list of messages, system prompt, and tools.

Examples:
2095
Was this page helpful?


Yes

No
Messages
List Models
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl https://api.anthropic.com/v1/messages/count_tokens \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-7-sonnet-20250219",
    "messages": [
        {"role": "user", "content": "Hello, world"}
    ]
}'

200

4XX

Copy
{
  "input_tokens": 2095
}Messages
Count Message tokens

Copy page

Count the number of tokens in a Message.

The Token Count API can be used to count the number of tokens in a Message, including tools, images, and documents, without creating it.

Learn more about token counting in our user guide

POST
/
v1
/
messages
/
count_tokens
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Body
application/json
​
messages
object[]required
Input messages.

Our models are trained to operate on alternating user and assistant conversational turns. When creating a new Message, you specify the prior conversational turns with the messages parameter, and the model then generates the next Message in the conversation. Consecutive user or assistant turns in your request will be combined into a single turn.

Each input message must be an object with a role and content. You can specify a single user-role message, or you can include multiple user and assistant messages.

If the final message uses the assistant role, the response content will continue immediately from the content in that message. This can be used to constrain part of the model's response.

Example with a single user message:

[{"role": "user", "content": "Hello, Claude"}]
Example with multiple conversational turns:

[
  {"role": "user", "content": "Hello there."},
  {"role": "assistant", "content": "Hi, I'm Claude. How can I help you?"},
  {"role": "user", "content": "Can you explain LLMs in plain English?"},
]
Example with a partially-filled response from Claude:

[
  {"role": "user", "content": "What's the Greek name for Sun? (A) Sol (B) Helios (C) Sun"},
  {"role": "assistant", "content": "The best answer is ("},
]
Each input message content may be either a single string or an array of content blocks, where each block has a specific type. Using a string for content is shorthand for an array of one content block of type "text". The following input messages are equivalent:

{"role": "user", "content": "Hello, Claude"}
{"role": "user", "content": [{"type": "text", "text": "Hello, Claude"}]}
Starting with Claude 3 models, you can also send image content blocks:

{"role": "user", "content": [
  {
    "type": "image",
    "source": {
      "type": "base64",
      "media_type": "image/jpeg",
      "data": "/9j/4AAQSkZJRg...",
    }
  },
  {"type": "text", "text": "What is in this image?"}
]}
We currently support the base64 source type for images, and the image/jpeg, image/png, image/gif, and image/webp media types.

See examples for more input examples.

Note that if you want to include a system prompt, you can use the top-level system parameter — there is no "system" role for input messages in the Messages API.

There is a limit of 100,000 messages in a single request.


Show child attributes

​
model
stringrequired
The model that will complete your prompt.

See models for additional details and options.

Required string length: 1 - 256
Examples:
"claude-3-7-sonnet-20250219"
​
mcp_servers
object[]
MCP servers to be utilized in this request


Show child attributes

​
system

string
System prompt.

A system prompt is a way of providing context and instructions to Claude, such as specifying a particular goal or role. See our guide to system prompts.

Examples:
[
  {
    "text": "Today's date is 2024-06-01.",
    "type": "text"
  }
]
"Today's date is 2023-01-01."

​
thinking
object
Configuration for enabling Claude's extended thinking.

When enabled, responses include thinking content blocks showing Claude's thinking process before the final answer. Requires a minimum budget of 1,024 tokens and counts towards your max_tokens limit.

See extended thinking for details.

Enabled
Disabled

Show child attributes

​
tool_choice
object
How the model should use the provided tools. The model can use a specific tool, any available tool, decide by itself, or not use tools at all.

Auto
Any
Tool
None

Show child attributes

​
tools
object[]
Definitions of tools that the model may use.

If you include tools in your API request, the model may return tool_use content blocks that represent the model's use of those tools. You can then run those tools using the tool input generated by the model and then optionally return results back to the model using tool_result content blocks.

Each tool definition includes:

name: Name of the tool.
description: Optional, but strongly-recommended description of the tool.
input_schema: JSON schema for the tool input shape that the model will produce in tool_use output content blocks.
For example, if you defined tools as:

[
  {
    "name": "get_stock_price",
    "description": "Get the current stock price for a given ticker symbol.",
    "input_schema": {
      "type": "object",
      "properties": {
        "ticker": {
          "type": "string",
          "description": "The stock ticker symbol, e.g. AAPL for Apple Inc."
        }
      },
      "required": ["ticker"]
    }
  }
]
And then asked the model "What's the S&P 500 at today?", the model might produce tool_use content blocks in the response like this:

[
  {
    "type": "tool_use",
    "id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "name": "get_stock_price",
    "input": { "ticker": "^GSPC" }
  }
]
You might then run your get_stock_price tool with {"ticker": "^GSPC"} as an input, and return the following back to the model in a subsequent user message:

[
  {
    "type": "tool_result",
    "tool_use_id": "toolu_01D7FLrfh4GYq7yT1ULFeyMV",
    "content": "259.75 USD"
  }
]
Tools can be used for workflows that include running client-side tools and functions, or more generally whenever you want the model to produce a particular JSON structure of output.

See our guide for more details.

Custom tool
Computer use tool (2024-01-22)
Bash tool (2024-10-22)
Text editor tool (2024-10-22)
Computer use tool (2025-01-24)
Bash tool (2025-01-24)
Text editor tool (2025-01-24)
TextEditor_20250429
Web search tool (2025-03-05)
Code execution tool (2025-05-22)

Show child attributes

Examples:
{
  "description": "Get the current weather in a given location",
  "input_schema": {
    "properties": {
      "location": {
        "description": "The city and state, e.g. San Francisco, CA",
        "type": "string"
      },
      "unit": {
        "description": "Unit for the output - one of (celsius, fahrenheit)",
        "type": "string"
      }
    },
    "required": ["location"],
    "type": "object"
  },
  "name": "get_weather"
}
Response
200

200
application/json
Successful Response
​
input_tokens
integerrequired
The total number of tokens across the provided list of messages, system prompt, and tools.

Examples:
2095
Was this page helpful?


Yes

No
Messages
List Models
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl https://api.anthropic.com/v1/messages/count_tokens \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-3-7-sonnet-20250219",
    "messages": [
        {"role": "user", "content": "Hello, world"}
    ]
}'

200

4XX

Copy
{
  "input_tokens": 2095
}



Message Batches
Create a Message Batch

Copy page

Send a batch of Message creation requests.

The Message Batches API can be used to process multiple Messages API requests at once. Once a Message Batch is created, it begins processing immediately. Batches can take up to 24 hours to complete.

Learn more about the Message Batches API in our user guide

POST
/
v1
/
messages
/
batches
​
Feature Support
The Message Batches API supports the following models: Claude Haiku 3, Claude Opus 3, Claude Sonnet 3.5, Claude Sonnet 3.5 v2, Claude Sonnet 3.7, Claude Sonnet 4, and Claude Opus 4. All features available in the Messages API, including beta features, are available through the Message Batches API.

Batches may contain up to 100,000 requests and be up to 256 MB in total size.

Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Body
application/json
​
requests
object[]required
List of requests for prompt completion. Each is an individual request to create a Message.


Show child attributes

Response
200

200
application/json
Successful Response
​
archived_at
string | nullrequired
RFC 3339 datetime string representing the time at which the Message Batch was archived and its results became unavailable.

Examples:
"2024-08-20T18:37:24.100435Z"
​
cancel_initiated_at
string | nullrequired
RFC 3339 datetime string representing the time at which cancellation was initiated for the Message Batch. Specified only if cancellation was initiated.

Examples:
"2024-08-20T18:37:24.100435Z"
​
created_at
stringrequired
RFC 3339 datetime string representing the time at which the Message Batch was created.

Examples:
"2024-08-20T18:37:24.100435Z"
​
ended_at
string | nullrequired
RFC 3339 datetime string representing the time at which processing for the Message Batch ended. Specified only once processing ends.

Processing ends when every request in a Message Batch has either succeeded, errored, canceled, or expired.

Examples:
"2024-08-20T18:37:24.100435Z"
​
expires_at
stringrequired
RFC 3339 datetime string representing the time at which the Message Batch will expire and end processing, which is 24 hours after creation.

Examples:
"2024-08-20T18:37:24.100435Z"
​
id
stringrequired
Unique object identifier.

The format and length of IDs may change over time.

Examples:
"msgbatch_013Zva2CMHLNnXjNJJKqJ2EF"
​
processing_status
enum<string>required
Processing status of the Message Batch.

Available options: in_progress, canceling, ended 
​
request_counts
objectrequired
Tallies requests within the Message Batch, categorized by their status.

Requests start as processing and move to one of the other statuses only once processing of the entire batch ends. The sum of all values always matches the total number of requests in the batch.


Show child attributes

​
results_url
string | nullrequired
URL to a .jsonl file containing the results of the Message Batch requests. Specified only once processing ends.

Results in the file are not guaranteed to be in the same order as requests. Use the custom_id field to match results to requests.

Examples:
"https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results"
​
type
enum<string>default:message_batchrequired
Object type.

For Message Batches, this is always "message_batch".

Available options: message_batch 
Was this page helpful?


Yes

No
Get a Model
Retrieve a Message Batch
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl https://api.anthropic.com/v1/messages/batches \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "requests": [
        {
            "custom_id": "my-first-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hello, world"}
                ]
            }
        },
        {
            "custom_id": "my-second-request",
            "params": {
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hi again, friend"}
                ]
            }
        }
    ]
}'

200

4XX

Copy
{
  "archived_at": "2024-08-20T18:37:24.100435Z",
  "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
  "created_at": "2024-08-20T18:37:24.100435Z",
  "ended_at": "2024-08-20T18:37:24.100435Z",
  "expires_at": "2024-08-20T18:37:24.100435Z",
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "processing_status": "in_progress",
  "request_counts": {
    "canceled": 10,
    "errored": 30,
    "expired": 10,
    "processing": 100,
    "succeeded": 50
  },
  "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
  "type": "message_batch"
}


Message Batches
Cancel a Message Batch

Copy page

Batches may be canceled any time before processing ends. Once cancellation is initiated, the batch enters a canceling state, at which time the system may complete any in-progress, non-interruptible requests before finalizing cancellation.

The number of canceled requests is specified in request_counts. To determine which requests were canceled, check the individual results within the batch. Note that cancellation may not result in any canceled requests if they were non-interruptible.

Learn more about the Message Batches API in our user guide

POST
/
v1
/
messages
/
batches
/
{message_batch_id}
/
cancel
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Path Parameters
​
message_batch_id
stringrequired
ID of the Message Batch.

Response
200

200
application/json
Successful Response
​
archived_at
string | nullrequired
RFC 3339 datetime string representing the time at which the Message Batch was archived and its results became unavailable.

Examples:
"2024-08-20T18:37:24.100435Z"
​
cancel_initiated_at
string | nullrequired
RFC 3339 datetime string representing the time at which cancellation was initiated for the Message Batch. Specified only if cancellation was initiated.

Examples:
"2024-08-20T18:37:24.100435Z"
​
created_at
stringrequired
RFC 3339 datetime string representing the time at which the Message Batch was created.

Examples:
"2024-08-20T18:37:24.100435Z"
​
ended_at
string | nullrequired
RFC 3339 datetime string representing the time at which processing for the Message Batch ended. Specified only once processing ends.

Processing ends when every request in a Message Batch has either succeeded, errored, canceled, or expired.

Examples:
"2024-08-20T18:37:24.100435Z"
​
expires_at
stringrequired
RFC 3339 datetime string representing the time at which the Message Batch will expire and end processing, which is 24 hours after creation.

Examples:
"2024-08-20T18:37:24.100435Z"
​
id
stringrequired
Unique object identifier.

The format and length of IDs may change over time.

Examples:
"msgbatch_013Zva2CMHLNnXjNJJKqJ2EF"
​
processing_status
enum<string>required
Processing status of the Message Batch.

Available options: in_progress, canceling, ended 
​
request_counts
objectrequired
Tallies requests within the Message Batch, categorized by their status.

Requests start as processing and move to one of the other statuses only once processing of the entire batch ends. The sum of all values always matches the total number of requests in the batch.


Show child attributes

​
results_url
string | nullrequired
URL to a .jsonl file containing the results of the Message Batch requests. Specified only once processing ends.

Results in the file are not guaranteed to be in the same order as requests. Use the custom_id field to match results to requests.

Examples:
"https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results"
​
type
enum<string>default:message_batchrequired
Object type.

For Message Batches, this is always "message_batch".

Available options: message_batch 
Was this page helpful?


Yes

No
List Message Batches
Delete a Message Batch
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl --request POST https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d/cancel \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01"

200

4XX

Copy
{
  "archived_at": "2024-08-20T18:37:24.100435Z",
  "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
  "created_at": "2024-08-20T18:37:24.100435Z",
  "ended_at": "2024-08-20T18:37:24.100435Z",
  "expires_at": "2024-08-20T18:37:24.100435Z",
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "processing_status": "in_progress",
  "request_counts": {
    "canceled": 10,
    "errored": 30,
    "expired": 10,
    "processing": 100,
    "succeeded": 50
  },
  "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
  "type": "message_batch"



  Message Batches
Retrieve a Message Batch

Copy page

This endpoint is idempotent and can be used to poll for Message Batch completion. To access the results of a Message Batch, make a request to the results_url field in the response.

Learn more about the Message Batches API in our user guide

GET
/
v1
/
messages
/
batches
/
{message_batch_id}
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Path Parameters
​
message_batch_id
stringrequired
ID of the Message Batch.

Response
200

200
application/json
Successful Response
​
archived_at
string | nullrequired
RFC 3339 datetime string representing the time at which the Message Batch was archived and its results became unavailable.

Examples:
"2024-08-20T18:37:24.100435Z"
​
cancel_initiated_at
string | nullrequired
RFC 3339 datetime string representing the time at which cancellation was initiated for the Message Batch. Specified only if cancellation was initiated.

Examples:
"2024-08-20T18:37:24.100435Z"
​
created_at
stringrequired
RFC 3339 datetime string representing the time at which the Message Batch was created.

Examples:
"2024-08-20T18:37:24.100435Z"
​
ended_at
string | nullrequired
RFC 3339 datetime string representing the time at which processing for the Message Batch ended. Specified only once processing ends.

Processing ends when every request in a Message Batch has either succeeded, errored, canceled, or expired.

Examples:
"2024-08-20T18:37:24.100435Z"
​
expires_at
stringrequired
RFC 3339 datetime string representing the time at which the Message Batch will expire and end processing, which is 24 hours after creation.

Examples:
"2024-08-20T18:37:24.100435Z"
​
id
stringrequired
Unique object identifier.

The format and length of IDs may change over time.

Examples:
"msgbatch_013Zva2CMHLNnXjNJJKqJ2EF"
​
processing_status
enum<string>required
Processing status of the Message Batch.

Available options: in_progress, canceling, ended 
​
request_counts
objectrequired
Tallies requests within the Message Batch, categorized by their status.

Requests start as processing and move to one of the other statuses only once processing of the entire batch ends. The sum of all values always matches the total number of requests in the batch.


Show child attributes

​
results_url
string | nullrequired
URL to a .jsonl file containing the results of the Message Batch requests. Specified only once processing ends.

Results in the file are not guaranteed to be in the same order as requests. Use the custom_id field to match results to requests.

Examples:
"https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results"
​
type
enum<string>default:message_batchrequired
Object type.

For Message Batches, this is always "message_batch".

Available options: message_batch 
Was this page helpful?


Yes

No
Create a Message Batch
Retrieve Message Batch Results
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01"

200

4XX

Copy
{
  "archived_at": "2024-08-20T18:37:24.100435Z",
  "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
  "created_at": "2024-08-20T18:37:24.100435Z",
  "ended_at": "2024-08-20T18:37:24.100435Z",
  "expires_at": "2024-08-20T18:37:24.100435Z",
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "processing_status": "in_progress",
  "request_counts": {
    "canceled": 10,
    "errored": 30,
    "expired": 10,
    "processing": 100,
    "succeeded": 50
  },
  "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
  "type": "message_batch"
}


Message Batches
Retrieve Message Batch Results

Copy page

Streams the results of a Message Batch as a .jsonl file.

Each line in the file is a JSON object containing the result of a single request in the Message Batch. Results are not guaranteed to be in the same order as requests. Use the custom_id field to match results to requests.

Learn more about the Message Batches API in our user guide

GET
/
v1
/
messages
/
batches
/
{message_batch_id}
/
results
The path for retrieving Message Batch results should be pulled from the batch’s results_url. This path should not be assumed and may change.
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Path Parameters
​
message_batch_id
stringrequired
ID of the Message Batch.

Response
200

200
application/x-jsonl
Successful Response
This is a single line in the response .jsonl file and does not represent the response as a whole.

​
custom_id
stringrequired
Developer-provided ID created for each request in a Message Batch. Useful for matching results to requests, as results may be given out of request order.

Must be unique for each request within the Message Batch.

Examples:
"my-custom-id-1"
​
result
objectrequired
Processing result for this request.

Contains a Message output if processing was successful, an error response if processing failed, or the reason why processing was not attempted, such as cancellation or expiration.

SucceededResult
ErroredResult
CanceledResult
ExpiredResult

Show child attributes

Was this page helpful?


Yes

No
Retrieve a Message Batch
List Message Batches
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d/results \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01"

200

4XX

Copy
{"custom_id":"my-second-request","result":{"type":"succeeded","message":{"id":"msg_014VwiXbi91y3JMjcpyGBHX5","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello again! It's nice to see you. How can I assist you today? Is there anything specific you'd like to chat about or any questions you have?"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":11,"output_tokens":36}}}}
{"custom_id":"my-first-request","result":{"type":"succeeded","message":{"id":"msg_01FqfsLoHwgeFbguDgpz48m7","type":"message","role":"assistant","model":"claude-3-5-sonnet-20240620","content":[{"type":"text","text":"Hello! How can I assist you today? Feel free to ask me any questions or let me know if there's anything you'd like to chat about."}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":10,"output_tokens":34}}}}



Message Batches
List Message Batches

Copy page

List all Message Batches within a Workspace. Most recently created batches are returned first.

Learn more about the Message Batches API in our user guide

GET
/
v1
/
messages
/
batches
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Query Parameters
​
before_id
string
ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately before this object.

​
after_id
string
ID of the object to use as a cursor for pagination. When provided, returns the page of results immediately after this object.

​
limit
integerdefault:20
Number of items to return per page.

Defaults to 20. Ranges from 1 to 1000.

Required range: 1 <= x <= 1000
Response
200

200
application/json
Successful Response
​
data
object[]required

Show child attributes

​
first_id
string | nullrequired
First ID in the data list. Can be used as the before_id for the previous page.

​
has_more
booleanrequired
Indicates if there are more results in the requested page direction.

​
last_id
string | nullrequired
Last ID in the data list. Can be used as the after_id for the next page.

Was this page helpful?


Yes

No
Retrieve Message Batch Results
Cancel a Message Batch
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl https://api.anthropic.com/v1/messages/batches \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01"

200

4XX

Copy
{
  "data": [
    {
      "archived_at": "2024-08-20T18:37:24.100435Z",
      "cancel_initiated_at": "2024-08-20T18:37:24.100435Z",
      "created_at": "2024-08-20T18:37:24.100435Z",
      "ended_at": "2024-08-20T18:37:24.100435Z",
      "expires_at": "2024-08-20T18:37:24.100435Z",
      "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
      "processing_status": "in_progress",
      "request_counts": {
        "canceled": 10,
        "errored": 30,
        "expired": 10,
        "processing": 100,
        "succeeded": 50
      },
      "results_url": "https://api.anthropic.com/v1/messages/batches/msgbatch_013Zva2CMHLNnXjNJJKqJ2EF/results",
      "type": "message_batch"
    }
  ],
  "first_id": "<string>",
  "has_more": true,
  "last_id": "<string>"
}

Message Batches
Delete a Message Batch

Copy page

Delete a Message Batch.

Message Batches can only be deleted once they’ve finished processing. If you’d like to delete an in-progress batch, you must first cancel it.

Learn more about the Message Batches API in our user guide

DELETE
/
v1
/
messages
/
batches
/
{message_batch_id}
Headers
​
anthropic-beta
string[]
Optional header to specify the beta version(s) you want to use.

To use multiple betas, use a comma separated list like beta1,beta2 or specify the header multiple times for each beta.

​
anthropic-version
stringrequired
The version of the Anthropic API you want to use.

Read more about versioning and our version history here.

​
x-api-key
stringrequired
Your unique API key for authentication.

This key is required in the header of all API requests, to authenticate your account and access Anthropic's services. Get your API key through the Console. Each key is scoped to a Workspace.

Path Parameters
​
message_batch_id
stringrequired
ID of the Message Batch.

Response
200

200
application/json
Successful Response
​
id
stringrequired
ID of the Message Batch.

Examples:
"msgbatch_013Zva2CMHLNnXjNJJKqJ2EF"
​
type
enum<string>default:message_batch_deletedrequired
Deleted object type.

For Message Batches, this is always "message_batch_deleted".

Available options: message_batch_deleted 
Was this page helpful?


Yes

No
Cancel a Message Batch
Create a File
x
linkedin

cURL

Python

JavaScript

PHP

Go

Java

Copy
curl -X DELETE https://api.anthropic.com/v1/messages/batches/msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01"

200

4XX

Copy
{
  "id": "msgbatch_013Zva2CMHLNnXjNJJKqJ2EF",
  "type": "message_batch_deleted"
}