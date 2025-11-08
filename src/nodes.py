# from colorama import Fore, Style
# from .agents import Agents
# from .tools.GmailTools import GmailToolsClass
# from .state import GraphState, Email


# class Nodes:
#     def __init__(self):
#         self.agents = Agents()
#         self.gmail_tools = GmailToolsClass()

#     def load_new_emails(self, state: GraphState) -> GraphState:
#         """Loads new emails from Gmail and updates the state."""
#         print(Fore.YELLOW + "Loading new emails...\n" + Style.RESET_ALL)
#         recent_emails = self.gmail_tools.fetch_unanswered_emails()
#         emails = [Email(**email) for email in recent_emails]
#         return {"emails": emails}

#     def check_new_emails(self, state: GraphState) -> str:
#         """Checks if there are new emails to process."""
#         if len(state['emails']) == 0:
#             print(Fore.RED + "No new emails" + Style.RESET_ALL)
#             return "empty"
#         else:
#             print(Fore.GREEN + "New emails to process" + Style.RESET_ALL)
#             return "process"
        
#     def is_email_inbox_empty(self, state: GraphState) -> GraphState:
#         return state

#     def categorize_email(self, state: GraphState) -> GraphState:
#         """Categorizes the current email using the categorize_email agent."""
#         print(Fore.YELLOW + "Checking email category...\n" + Style.RESET_ALL)
        
#         # Get the last email
#         current_email = state["emails"][-1]
#         result = self.agents.categorize_email.invoke({"email": current_email.body})
#         print(Fore.MAGENTA + f"Email category: {result.category.value}" + Style.RESET_ALL)
        
#         return {
#             "email_category": result.category.value,
#             "current_email": current_email
#         }

#     def route_email_based_on_category(self, state: GraphState) -> str:
#         """Routes the email based on its category."""
#         print(Fore.YELLOW + "Routing email based on category...\n" + Style.RESET_ALL)
#         category = state["email_category"]
#         if category == "product_enquiry":
#             return "product related"
#         elif category == "unrelated":
#             return "unrelated"
#         else:
#             return "not product related"

#     def construct_rag_queries(self, state: GraphState) -> GraphState:
#         """Constructs RAG queries based on the email content."""
#         print(Fore.YELLOW + "Designing RAG query...\n" + Style.RESET_ALL)
#         email_content = state["current_email"].body
#         query_result = self.agents.design_rag_queries.invoke({"email": email_content})
        
#         return {"rag_queries": query_result.queries}

#     def retrieve_from_rag(self, state: GraphState) -> GraphState:
#         """Retrieves information from internal knowledge based on RAG questions."""
#         print(Fore.YELLOW + "Retrieving information from internal knowledge...\n" + Style.RESET_ALL)
#         final_answer = ""
#         for query in state["rag_queries"]:
#             rag_result = self.agents.generate_rag_answer.invoke(query)
#             final_answer += query + "\n" + rag_result + "\n\n"
        
#         return {"retrieved_documents": final_answer}

#     def write_draft_email(self, state: GraphState) -> GraphState:
#         """Writes a draft email based on the current email and retrieved information."""
#         print(Fore.YELLOW + "Writing draft email...\n" + Style.RESET_ALL)
        
#         # Format input to the writer agent
#         inputs = (
#             f'# **EMAIL CATEGORY:** {state["email_category"]}\n\n'
#             f'# **EMAIL CONTENT:**\n{state["current_email"].body}\n\n'
#             f'# **INFORMATION:**\n{state["retrieved_documents"]}' # Empty for feedback or complaint
#         )
        
#         # Get messages history for current email
#         writer_messages = state.get('writer_messages', [])
        
#         # Write email
#         draft_result = self.agents.email_writer.invoke({
#             "email_information": inputs,
#             "history": writer_messages
#         })
#         email = draft_result.email
#         trials = state.get('trials', 0) + 1

#         # Append writer's draft to the message list
#         writer_messages.append(f"**Draft {trials}:**\n{email}")

#         return {
#             "generated_email": email, 
#             "trials": trials,
#             "writer_messages": writer_messages
#         }

#     def verify_generated_email(self, state: GraphState) -> GraphState:
#         """Verifies the generated email using the proofreader agent."""
#         print(Fore.YELLOW + "Verifying generated email...\n" + Style.RESET_ALL)
#         review = self.agents.email_proofreader.invoke({
#             "initial_email": state["current_email"].body,
#             "generated_email": state["generated_email"],
#         })

#         writer_messages = state.get('writer_messages', [])
#         writer_messages.append(f"**Proofreader Feedback:**\n{review.feedback}")

#         return {
#             "sendable": review.send,
#             "writer_messages": writer_messages
#         }

#     def must_rewrite(self, state: GraphState) -> str:
#         """Determines if the email needs to be rewritten based on the review and trial count."""
#         email_sendable = state["sendable"]
#         if email_sendable:
#             print(Fore.GREEN + "Email is good, ready to be sent!!!" + Style.RESET_ALL)
#             state["emails"].pop()
#             state["writer_messages"] = []
#             return "send"
#         elif state["trials"] >= 3:
#             print(Fore.RED + "Email is not good, we reached max trials must stop!!!" + Style.RESET_ALL)
#             state["emails"].pop()
#             state["writer_messages"] = []
#             return "stop"
#         else:
#             print(Fore.RED + "Email is not good, must rewrite it..." + Style.RESET_ALL)
#             return "rewrite"

#     def create_draft_response(self, state: GraphState) -> GraphState:
#         """Creates a draft response in Gmail."""
#         print(Fore.YELLOW + "Creating draft email...\n" + Style.RESET_ALL)
#         self.gmail_tools.create_draft_reply(state["current_email"], state["generated_email"])
        
#         return {"retrieved_documents": "", "trials": 0}

#     def send_email_response(self, state: GraphState) -> GraphState:
#         """Sends the email response directly using Gmail."""
#         print(Fore.YELLOW + "Sending email...\n" + Style.RESET_ALL)
#         self.gmail_tools.send_reply(state["current_email"], state["generated_email"])
        
#         return {"retrieved_documents": "", "trials": 0}
    
#     def skip_unrelated_email(self, state):
#         """Skip unrelated email and remove from emails list."""
#         print("Skipping unrelated email...\n")
#         state["emails"].pop()
#         return state





















##SECOND DRAFT
# from colorama import Fore, Style
# from .agents import Agents
# from .tools.GmailTools import GmailToolsClass
# from .state import GraphState, Email

# ##CHANGE MADE##
# # Import HumanMessage to build multimodal prompts (text + images)
# # Import all prompts so we can format them within the nodes.
# from langchain_core.messages import HumanMessage
# from .prompts import (
#     CATEGORIZE_EMAIL_PROMPT, 
#     GENERATE_RAG_QUERIES_PROMPT, 
#     EMAIL_WRITER_PROMPT, 
#     EMAIL_PROOFREADER_PROMPT
# )
# ##CHANGE MADE##


# class Nodes:
#     def __init__(self):
#         self.agents = Agents()
#         self.gmail_tools = GmailToolsClass()

#     ##CHANGE MADE##
#     # Add a helper function to build the list of content for a HumanMessage
#     def _build_multimodal_content(self, text_prompt: str, email: Email):
#         """Helper to build the message content list for the LLM."""
        
#         # Start with the text part
#         content = [{"type": "text", "text": text_prompt}]
        
#         # Add all images from attachments
#         for img_base64 in email.attachment_images:
#             content.append(
#                 {
#                     "type": "image_url",
#                     "image_url": {
#                         # Prepend the required data URI prefix for base64 images
#                         "url": f"data:image/jpeg;base64,{img_base64}"
#                     }
#                 }
#             )
#         return content
#     ##CHANGE MADE##

#     def load_new_emails(self, state: GraphState) -> GraphState:
#         """Loads new emails from Gmail and updates the state."""
#         print(Fore.YELLOW + "Loading new emails...\n" + Style.RESET_ALL)
#         recent_emails = self.gmail_tools.fetch_unanswered_emails()
#         ##CHANGE MADE##
#         # The Email class now expects 'attachment_images'.
#         # Our modified _get_email_info in GmailToolsClass provides this.
#         # We also add a default empty list for 'attachment_images' just in case.
#         emails = [Email(**{**email, 'attachment_images': email.get('attachment_images', [])}) for email in recent_emails]
#         ##CHANGE MADE##
#         return {"emails": emails}

#     def check_new_emails(self, state: GraphState) -> str:
#         """Checks if there are new emails to process."""
#         if len(state['emails']) == 0:
#             print(Fore.RED + "No new emails" + Style.RESET_ALL)
#             return "empty"
#         else:
#             print(Fore.GREEN + "New emails to process" + Style.RESET_ALL)
#             return "process"
        
#     def is_email_inbox_empty(self, state: GraphState) -> GraphState:
#         return state

#     def categorize_email(self, state: GraphState) -> GraphState:
#         """Categorizes the current email using the categorize_email agent."""
#         print(Fore.YELLOW + "Checking email category...\n" + Style.RESET_ALL)
        
#         # Get the last email
#         current_email = state["emails"][-1]

#         ##CHANGE MADE##
#         # We now build a multimodal prompt.
        
#         # 1. Format the text part of the prompt
#         prompt_text = CATEGORIZE_EMAIL_PROMPT.format(email=current_email.body)
        
#         # 2. Build the full message content (text + images)
#         message_content = self._build_multimodal_content(prompt_text, current_email)
        
#         # 3. Create the HumanMessage
#         prompt = HumanMessage(content=message_content)

#         # 4. Invoke the agent (which is now just gemini + structured output)
#         result = self.agents.categorize_email.invoke(prompt)
#         ##CHANGE MADE##
        
#         print(Fore.MAGENTA + f"Email category: {result.category.value}" + Style.RESET_ALL)
        
#         return {
#             "email_category": result.category.value,
#             "current_email": current_email
#         }

#     def route_email_based_on_category(self, state: GraphState) -> str:
#         """Routes the email based on its category."""
#         print(Fore.YELLOW + "Routing email based on category...\n" + Style.RESET_ALL)
#         category = state["email_category"]
#         if category == "product_enquiry":
#             return "product related"
#         elif category == "unrelated":
#             return "unrelated"
#         else:
#             return "not product related"

#     def construct_rag_queries(self, state: GraphState) -> GraphState:
#         """Constructs RAG queries based on the email content."""
#         print(Fore.YELLOW + "Designing RAG query...\n" + Style.RESET_ALL)
        
#         ##CHANGE MADE##
#         # We build a multimodal prompt for the RAG query designer.
        
#         # 1. Get the current email
#         current_email = state["current_email"]
        
#         # 2. Format the text part of the prompt
#         prompt_text = GENERATE_RAG_QUERIES_PROMPT.format(email=current_email.body)
        
#         # 3. Build the full message content (text + images)
#         message_content = self._build_multimodal_content(prompt_text, current_email)
        
#         # 4. Create the HumanMessage
#         prompt = HumanMessage(content=message_content)

#         # 5. Invoke the agent
#         query_result = self.agents.design_rag_queries.invoke(prompt)
#         ##CHANGE MADE##
        
#         return {"rag_queries": query_result.queries}

#     def retrieve_from_rag(self, state: GraphState) -> GraphState:
#         """Retrieves information from internal knowledge based on RAG questions."""
#         print(Fore.YELLOW + "Retrieving information from internal knowledge...\n" + Style.RESET_ALL)
#         final_answer = ""
#         for query in state["rag_queries"]:
#             # This agent is text-only (llama) and is working as intended. No changes needed.
#             rag_result = self.agents.generate_rag_answer.invoke(query)
#             final_answer += query + "\n" + rag_result + "\n\n"
        
#         return {"retrieved_documents": final_answer}

#     def write_draft_email(self, state: GraphState) -> GraphState:
#         """Writes a draft email based on the current email and retrieved information."""
#         print(Fore.YELLOW + "Writing draft email...\n" + Style.RESET_ALL)
        
#         ##CHANGE MADE##
#         # This node now builds a full message history for the multimodal writer agent.
#         current_email = state["current_email"]
        
#         # 1. Format the text input for the HUMAN turn
#         inputs = (
#             f'# **EMAIL CATEGORY:** {state["email_category"]}\n\n'
#             f'# **EMAIL CONTENT:**\n{current_email.body}\n\n'
#             f'# **ATTACHMENT CONTENT:**\n(See attached images)\n\n'
#             f'# **INFORMATION:**\n{state["retrieved_documents"]}' # Empty for feedback or complaint
#         )
        
#         # 2. Get messages history for current email
#         writer_messages = state.get('writer_messages', [])
        
#         # 3. Build the multimodal content for the HUMAN turn
#         human_content = self._build_multimodal_content(inputs, current_email)
        
#         # 4. Create the full message list: [System, History..., Human]
#         message_list = [
#             # The System prompt
#             HumanMessage(content=EMAIL_WRITER_PROMPT),
#             # The History
#             *writer_messages,
#             # The new Human prompt
#             HumanMessage(content=human_content)
#         ]
        
#         # 5. Write email
#         draft_result = self.agents.email_writer.invoke(message_list)
#         email = draft_result.email
#         trials = state.get('trials', 0) + 1

#         # 6. Append writer's draft to the message list
#         writer_messages.append(f"**Draft {trials}:**\n{email}")
#         ##CHANGE MADE##

#         return {
#             "generated_email": email, 
#             "trials": trials,
#             "writer_messages": writer_messages
#         }

#     def verify_generated_email(self, state: GraphState) -> GraphState:
#         """Verifies the generated email using the proofreader agent."""
#         print(Fore.YELLOW + "Verifying generated email...\n" + Style.RESET_ALL)
        
#         ##CHANGE MADE##
#         # Build the multimodal prompt for the proofreader
#         current_email = state["current_email"]
        
#         # 1. Format the text input
#         prompt_text = EMAIL_PROOFREADER_PROMPT.format(
#             initial_email=current_email.body,
#             generated_email=state["generated_email"]
#         )
        
#         # 2. Build the multimodal content
#         message_content = self._build_multimodal_content(prompt_text, current_email)
        
#         # 3. Create the HumanMessage
#         prompt = HumanMessage(content=message_content)

#         # 4. Invoke the proofreader agent
#         review = self.agents.email_proofreader.invoke(prompt)
#         ##CHANGE MADE##

#         writer_messages = state.get('writer_messages', [])
#         writer_messages.append(f"**Proofreader Feedback:**\n{review.feedback}")

#         return {
#             "sendable": review.send,
#             "writer_messages": writer_messages
#         }

#     def must_rewrite(self, state: GraphState) -> str:
#         """Determines if the email needs to be rewritten based on the review and trial count."""
#         email_sendable = state["sendable"]
#         if email_sendable:
#             print(Fore.GREEN + "Email is good, ready to be sent!!!" + Style.RESET_ALL)
#             state["emails"].pop()
#             state["writer_messages"] = []
#             return "send"
#         elif state["trials"] >= 3:
#             print(Fore.RED + "Email is not good, we reached max trials must stop!!!" + Style.RESET_ALL)
#             state["emails"].pop()
#             state["writer_messages"] = []
#             return "stop"
#         else:
#             print(Fore.RED + "Email is not good, must rewrite it..." + Style.RESET_ALL)
#             return "rewrite"

#     def create_draft_response(self, state: GraphState) -> GraphState:
#         """Creates a draft response in Gmail."""
#         print(Fore.YELLOW + "Creating draft email...\n" + Style.RESET_ALL)
#         self.gmail_tools.create_draft_reply(state["current_email"], state["generated_email"])
        
#         return {"retrieved_documents": "", "trials": 0}

#     def send_email_response(self, state: GraphState) -> GraphState:
#         """Sends the email response directly using Gmail."""
#         print(Fore.YELLOW + "Sending email...\n" + Style.RESET_ALL)
#         self.gmail_tools.send_reply(state["current_email"], state["generated_email"])
        
#         return {"retrieved_documents": "", "trials": 0}
    
#     def skip_unrelated_email(self, state):
#         """Skip unrelated email and remove from emails list."""
#         print("Skipping unrelated email...\n")
#         state["emails"].pop()
#         return state

from colorama import Fore, Style
from .agents import Agents
from .tools.GmailTools import GmailToolsClass
from .state import GraphState, Email
import json
import time

##CHANGE MADE##
# Import SystemMessage, HumanMessage, and AIMessage to correctly build
# the message lists for the multimodal LLM.
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .prompts import (
    CATEGORIZE_EMAIL_PROMPT, 
    GENERATE_RAG_QUERIES_PROMPT, 
    EMAIL_WRITER_PROMPT, 
    EMAIL_PROOFREADER_PROMPT
)
##CHANGE MADE##


class Nodes:
    def __init__(self):
        self.agents = Agents()
        self.gmail_tools = GmailToolsClass()

    ##CHANGE MADE##
    # Add a helper function to build the list of content for a HumanMessage
    def _build_multimodal_content(self, text_prompt: str, email: Email):
        """Helper to build the message content list for the LLM."""
        
        # Start with the text part
        content = [{"type": "text", "text": text_prompt}]
        
        # Add all images from attachments
        for img_base64 in email.attachment_images:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        # Prepend the required data URI prefix for base64 images
                        "url": f"data:image/jpeg;base64,{img_base64}"
                    }
                }
            )
        return content
    ##CHANGE MADE##

    def load_new_emails(self, state: GraphState) -> GraphState:
        """Loads new emails from Gmail and updates the state."""
        print(Fore.YELLOW + "Loading new emails...\n" + Style.RESET_ALL)
        recent_emails = self.gmail_tools.fetch_unanswered_emails()
        ##CHANGE MADE##
        # The Email class now expects 'attachment_images'.
        # Our modified _get_email_info in GmailToolsClass provides this.
        # We also add a default empty list for 'attachment_images' just in case.
        emails = [Email(**{**email, 'attachment_images': email.get('attachment_images', [])}) for email in recent_emails]
        ##CHANGE MADE##
        # Print a short summary of loaded emails for debugging (sender -> to)
        for e in emails:
            try:
                print(Fore.CYAN + f"Loaded email: from={e.sender} to={getattr(e, 'to', '')} subject={e.subject}" + Style.RESET_ALL)
            except Exception:
                # Be robust if any field is missing
                print(Fore.CYAN + f"Loaded email: summary unavailable" + Style.RESET_ALL)

        return {"emails": emails}

    def check_new_emails(self, state: GraphState) -> str:
        """Checks if there are new emails to process."""
        if len(state['emails']) == 0:
            print(Fore.RED + "No new emails" + Style.RESET_ALL)
            return "empty"
        else:
            print(Fore.GREEN + "New emails to process" + Style.RESET_ALL)
            return "process"
        
    def is_email_inbox_empty(self, state: GraphState) -> GraphState:
        return state

    def categorize_email(self, state: GraphState) -> GraphState:
        """Categorizes the current email using the categorize_email agent."""
        print(Fore.YELLOW + "Checking email category...\n" + Style.RESET_ALL)
        
        # Get the last email
        current_email = state["emails"][-1]

        ##CHANGE MADE##
        # We now build a multimodal prompt for the 'gemini' agent.
        
        # Print current email details for debugging
        try:
            print(Fore.CYAN + f"Processing email now: from={current_email.sender} to={getattr(current_email,'to','')} subject={current_email.subject}" + Style.RESET_ALL)
        except Exception:
            pass

        # 1. Format the text part of the prompt
        # Use simple replacement instead of str.format because the prompt
        # contains literal JSON braces (e.g. {"category": "..."}) which
        # would be interpreted as format placeholders and raise KeyError.
        prompt_text = CATEGORIZE_EMAIL_PROMPT.replace("{email}", current_email.body)
        
        # 2. Build the full message content (text + images)
        message_content = self._build_multimodal_content(prompt_text, current_email)
        
        # 3. Create the HumanMessage
        prompt = HumanMessage(content=message_content)

        # 4. Invoke the agent. We wrap the single 'prompt' in a list []
        #    to match what the model expects. Add retries and robust parsing
        #    so the pipeline doesn't crash on unexpected outputs.
        max_attempts = 3
        raw_result = None
        for attempt in range(1, max_attempts + 1):
            try:
                raw_result = self.agents.categorize_email.invoke([prompt])
            except Exception as e:
                print(Fore.RED + f"Error invoking categorize_email agent (attempt {attempt}): {e}" + Style.RESET_ALL)
                raw_result = None

            # If we got something truthy, break and try to parse it
            if raw_result:
                break

            # small backoff before retrying
            if attempt < max_attempts:
                time.sleep(0.5)

        # Try to extract category from the agent result in several ways.
        category_value = None

        # 1) If the structured output is present with attribute 'category'
        if raw_result is not None and hasattr(raw_result, 'category'):
            try:
                # Some structured wrappers expose `category` as an Enum-like
                # object with a `value` attribute; others might be plain strings.
                cat_attr = getattr(raw_result, 'category')
                category_value = getattr(cat_attr, 'value', cat_attr)
                if isinstance(category_value, bytes):
                    category_value = category_value.decode('utf-8')
            except Exception:
                category_value = None

        # 2) If the model returned a dict-like or simple mapping
        if category_value is None:
            try:
                # Some runtimes return plain dicts
                if isinstance(raw_result, dict):
                    category_value = raw_result.get('category') or raw_result.get('label')
            except Exception:
                pass

        # 3) If the model returned a string, try to parse JSON or match known keywords
        if category_value is None and isinstance(raw_result, str):
            # Try JSON parse first
            try:
                parsed = json.loads(raw_result)
                if isinstance(parsed, dict):
                    category_value = parsed.get('category') or parsed.get('label')
            except Exception:
                # not JSON; attempt simple substring matching for known categories
                lowered = raw_result.lower()
                for candidate in [
                    'legal_contractdraftrequest', 'contractdraftrequest', 'contract draft request',
                    'contract_review', 'contract review', 'legal_query', 'legal query',
                    'unrelated', 'other'
                ]:
                    if candidate in lowered:
                        category_value = candidate
                        break

        # Final fallback: if still unknown, log and set 'other'
        if not category_value:
            print(Fore.RED + "categorize_email returned no structured category after retries." + Style.RESET_ALL)
            try:
                print(Fore.RED + f"Raw agent result repr: {repr(raw_result)}" + Style.RESET_ALL)
            except Exception:
                pass
            category_value = 'other'
            print(Fore.MAGENTA + f"Email category: {category_value} (fallback)" + Style.RESET_ALL)
            return {
                'email_category': category_value,
                'current_email': current_email
            }

        # Normalize some known variations to the enum-like values used elsewhere
        normalized = str(category_value).strip()
        normalized_map = {
            'contract draft request': 'legal_contractDraftRequest',
            'contractdraftrequest': 'legal_contractDraftRequest',
            'legal_contractdraftrequest': 'legal_contractDraftRequest',
            'contract review': 'contract_review',
            'contract_review': 'contract_review',
            'legal query': 'legal_query',
            'legal_query': 'legal_query',
            'unrelated': 'unrelated',
            'other': 'other'
        }
        normalized_lower = normalized.lower()
        final_category = normalized_map.get(normalized_lower, normalized)

        print(Fore.MAGENTA + f"Email category: {final_category}" + Style.RESET_ALL)

        return {
            'email_category': final_category,
            'current_email': current_email
        }

    def route_email_based_on_category(self, state: GraphState) -> str:
        """Routes the email based on its category."""
        print(Fore.YELLOW + "Routing email based on category...\n" + Style.RESET_ALL)
        category = state["email_category"]
        if category == "legal_contractDraftRequest":
            return "contract draft request"
        elif category == "contract_review":
            return "contract review"
        elif category == "legal_query":
            return "legal query"
        elif category == "unrelated":
            return "unrelated"
        else:
            return "other"

    def construct_rag_queries(self, state: GraphState) -> GraphState:
        """Constructs RAG queries based on the email content."""
        print(Fore.YELLOW + "Designing RAG query...\n" + Style.RESET_ALL)
        
        ##CHANGE MADE##
        # We build a multimodal prompt for the RAG query designer ('gemini').
        
        # 1. Get the current email
        current_email = state["current_email"]
        
        # 2. Format the text part of the prompt
        # Use replace to avoid format() interpreting braces inside the prompt
        prompt_text = GENERATE_RAG_QUERIES_PROMPT.replace("{email}", current_email.body)
        
        # 3. Build the full message content (text + images)
        message_content = self._build_multimodal_content(prompt_text, current_email)
        
        # 4. Create the HumanMessage
        prompt = HumanMessage(content=message_content)

        # 5. Invoke the agent. We wrap the single 'prompt' in a list [].
        query_result = self.agents.design_rag_queries.invoke([prompt])
        ##CHANGE MADE##
        
        return {"rag_queries": query_result.queries}

    def retrieve_from_rag(self, state: GraphState) -> GraphState:
        """Retrieves information from internal knowledge based on RAG questions."""
        print(Fore.YELLOW + "Retrieving information from internal knowledge...\n" + Style.RESET_ALL)
        final_answer = ""
        for query in state["rag_queries"]:
            # This agent is text-only (llama) and is working as intended. No changes needed.
            rag_result = self.agents.generate_rag_answer.invoke(query)
            final_answer += query + "\n" + rag_result + "\n\n"
        
        return {"retrieved_documents": final_answer}

    def write_draft_email(self, state: GraphState) -> GraphState:
        """Writes a draft email based on the current email and retrieved information."""
        print(Fore.YELLOW + "Writing draft email...\n" + Style.RESET_ALL)
        
        ##CHANGE MADE##
        # This node now builds a full message history for the multimodal 'gemini' writer agent.
        current_email = state["current_email"]
        
        # 1. Format the text input for the HUMAN turn
        inputs = (
            f'# **EMAIL CATEGORY:** {state["email_category"]}\n\n'
            f'# **EMAIL CONTENT:**\n{current_email.body}\n\n'
            f'# **ATTACHMENT CONTENT:**\n(See attached images)\n\n'
            f'# **INFORMATION:**\n{state["retrieved_documents"]}' # Empty for feedback or complaint
        )
        
        # 2. Get messages history for current email
        writer_messages = state.get('writer_messages', [])
        
        # 3. Build the multimodal content for the HUMAN turn
        human_content = self._build_multimodal_content(inputs, current_email)
        
        # 4. Create the full message list: [System, History..., Human]
        message_list = [
            # The System prompt
            SystemMessage(content=EMAIL_WRITER_PROMPT),
            # The History
            *writer_messages,
            # The new Human prompt
            HumanMessage(content=human_content)
        ]
        
        # 5. Write email
        draft_result = self.agents.email_writer.invoke(message_list)
        email = draft_result.email
        trials = state.get('trials', 0) + 1

        # 6. Append writer's draft to the message list as an AIMessage
        writer_messages.append(AIMessage(content=f"**Draft {trials}:**\n{email}"))
        ##CHANGE MADE##

        return {
            "generated_email": email, 
            "trials": trials,
            "writer_messages": writer_messages
        }

    def verify_generated_email(self, state: GraphState) -> GraphState:
        """Verifies the generated email using the proofreader agent."""
        print(Fore.YELLOW + "Verifying generated email...\n" + Style.RESET_ALL)
        
        ##CHANGE MADE##
        # Build the multimodal prompt for the 'gemini' proofreader
        current_email = state["current_email"]
        
        # 1. Format the text input
        # Use replace rather than format to avoid KeyError from literal braces
        prompt_text = EMAIL_PROOFREADER_PROMPT.replace("{initial_email}", current_email.body).replace("{generated_email}", state["generated_email"])
        
        # 2. Build the multimodal content
        message_content = self._build_multimodal_content(prompt_text, current_email)
        
        # 3. Create the HumanMessage
        prompt = HumanMessage(content=message_content)

        # 4. Invoke the proofreader agent. We wrap the single 'prompt' in a list [].
        review = self.agents.email_proofreader.invoke([prompt])

        # 5. Add feedback to history as a HumanMessage (it's the proofreader's "turn")
        writer_messages = state.get('writer_messages', [])
        writer_messages.append(HumanMessage(content=f"**Proofreader Feedback:**\n{review.feedback}"))
        ##CHANGE MADE##

        return {
            "sendable": review.send,
            "writer_messages": writer_messages
        }

    def must_rewrite(self, state: GraphState) -> str:
        """Determines if the email needs to be rewritten based on the review and trial count."""
        email_sendable = state["sendable"]
        if email_sendable:
            print(Fore.GREEN + "Email is good, ready to be sent!!!" + Style.RESET_ALL)
            state["emails"].pop()
            state["writer_messages"] = []
            return "send"
        elif state["trials"] >= 3:
            print(Fore.RED + "Email is not good, we reached max trials must stop!!!" + Style.RESET_ALL)
            state["emails"].pop()
            state["writer_messages"] = []
            return "stop"
        else:
            print(Fore.RED + "Email is not good, must rewrite it..." + Style.RESET_ALL)
            return "rewrite"

    def create_draft_response(self, state: GraphState) -> GraphState:
        """Creates a draft response in Gmail."""
        print(Fore.YELLOW + "Creating draft email...\n" + Style.RESET_ALL)
        self.gmail_tools.create_draft_reply(state["current_email"], state["generated_email"])
        
        return {"retrieved_documents": "", "trials": 0}

    def send_email_response(self, state: GraphState) -> GraphState:
        """Sends the email response directly using Gmail."""
        print(Fore.YELLOW + "Sending email...\n" + Style.RESET_ALL)
        self.gmail_tools.send_reply(state["current_email"], state["generated_email"])
        
        return {"retrieved_documents": "", "trials": 0}
    
    def skip_unrelated_email(self, state):
        """Skip unrelated email and remove from emails list."""
        # Print which email is being skipped for easier debugging
        current = None
        if state.get("current_email"):
            current = state.get("current_email")
        elif state.get("emails"):
            current = state["emails"][-1]

        if current:
            try:
                print(Fore.YELLOW + f"Skipping unrelated email from={current.sender} to={getattr(current,'to','')} subject={current.subject}\n" + Style.RESET_ALL)
            except Exception:
                print(Fore.YELLOW + "Skipping unrelated email (summary unavailable)\n" + Style.RESET_ALL)

            # Mark the message as read in Gmail so it won't be fetched again
            try:
                msg_id = getattr(current, 'id', None)
                if msg_id:
                    self.gmail_tools.mark_as_read(msg_id)
            except Exception as e:
                print(Fore.RED + f"Failed to mark message as read: {e}" + Style.RESET_ALL)

        else:
            print(Fore.YELLOW + "Skipping unrelated email...\n" + Style.RESET_ALL)

        # Remove from local queue
        if state.get("emails"):
            state["emails"].pop()

        return state
    