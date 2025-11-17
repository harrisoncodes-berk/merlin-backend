# Response(
#     id="resp_02a8d91c764bad3000691a88a0e5b081a29ccfe36081c00f55",
#     created_at=1763346592.0,
#     error=None,
#     incomplete_details=None,
#     instructions=None,
#     metadata={},
#     model="gpt-4o-mini-2024-07-18",
#     object="response",
#     output=[
#         ResponseFunctionToolCall(
#             arguments='{"summary":"You have infiltrated Stormspire Keep, overheard a conversation about the princess\'s arrival, grabbed a rusted key from a nearby table, and are now moving deeper into the castle. The corridor is dimly lit, with distant voices echoing around you. You continue down the corridor, the sound of your footsteps muffled by the damp stone floor.","location":"Inside Stormspire Keep, a narrow corridor leading deeper into the castle.","combat_state":false}',
#             call_id="call_B7QR43u0wDmmZQt8o7Yc46lj",
#             name="update_adventure_status",
#             type="function_call",
#             id="fc_02a8d91c764bad3000691a88a1481881a280e10254ecae7449",
#             status="completed",
#         )
#     ],
#     parallel_tool_calls=True,
#     temperature=0.7,
#     tool_choice="auto",
#     tools=[
#         FunctionTool(
#             name="update_adventure_status",
#             parameters={
#                 "type": "object",
#                 "properties": {
#                     "summary": {
#                         "type": "string",
#                         "description": "An ongoing summary of what the character has done and what has happened in the story so far.",
#                         "max_length": 1000,
#                     },
#                     "location": {
#                         "type": "string",
#                         "description": "A short description of the character's current location.",
#                         "max_length": 100,
#                     },
#                     "combat_state": {
#                         "type": "boolean",
#                         "description": "True if the character is in combat, false otherwise.",
#                     },
#                 },
#                 "required": ["summary", "location", "combat_state"],
#                 "additionalProperties": False,
#             },
#             strict=True,
#             type="function",
#             description="Update the adventure status based on the latest user message. Does not require a followup.",
#         )
#     ],
#     top_p=1.0,
#     background=False,
#     conversation=None,
#     max_output_tokens=700,
#     max_tool_calls=None,
#     previous_response_id=None,
#     prompt=None,
#     prompt_cache_key=None,
#     reasoning=Reasoning(effort=None, generate_summary=None, summary=None),
#     safety_identifier=None,
#     service_tier="default",
#     status="completed",
#     text=ResponseTextConfig(
#         format=ResponseFormatJSONObject(type="json_object"), verbosity="medium"
#     ),
#     top_logprobs=0,
#     truncation="disabled",
#     usage=ResponseUsage(
#         input_tokens=1055,
#         input_tokens_details=InputTokensDetails(cached_tokens=0),
#         output_tokens=107,
#         output_tokens_details=OutputTokensDetails(reasoning_tokens=0),
#         total_tokens=1162,
#     ),
#     user=None,
#     billing={"payer": "developer"},
#     prompt_cache_retention=None,
#     store=True,
# )
