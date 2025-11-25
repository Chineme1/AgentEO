from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff
from crewai_tools import FileReadTool
import json
import os
from typing import List, Dict, Any, Callable
from pydantic import SkipValidation
from datetime import date, datetime

from gmail_crew_ai.tools.gmail_tools import GetUnreadEmailsTool, SaveDraftTool, GmailOrganizeTool, GmailDeleteTool, EmptyTrashTool, TotalEmailTool
from gmail_crew_ai.tools.slack_tool import SlackNotificationTool
from gmail_crew_ai.tools.date_tools import DateCalculationTool
from gmail_crew_ai.models import CategorizedEmail, OrganizedEmail, EmailResponse, SlackNotification, EmailCleanupInfo, SimpleCategorizedEmail, EmailDetails
from dotenv import load_dotenv


@CrewBase
class GmailCrewAi():
	"""Crew that processes emails."""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'
	print("IN here 3")
	@before_kickoff
	def fetch_emails(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
		"""Fetch emails before starting the crew and calculate ages."""
		print("Fetching emails before starting the crew...")
		print("IN here 4")
		# Get the email limit from inputs
		email_limit = inputs.get('email_limit', 5)
		print(f"Fetching {email_limit} emails...")
		print("IN here 5")
		# Create the output directory if it doesn't exist
		os.makedirs("output", exist_ok=True)
		print("IN here 6")
		# Use the GetUnreadEmailsTool directly
		email_tool = GetUnreadEmailsTool()
		email_tuples = email_tool._run(limit=email_limit)
		print("IN here 7")
		tool = TotalEmailTool()
		count = tool._run() #This is the total count of E-mails
		print("The Total Number of E-mails are: ", count)

		# Convert email tuples to EmailDetails objects with pre-calculated ages
		emails = []
		today = date.today()
		print("IN here 8")
		for email_tuple in email_tuples: # This is the email tool and the details about it.
			print("IN here 9")
			email_detail = EmailDetails.from_email_tuple(email_tuple)
			print("IN here 10")
			# Calculate age if date is available
			if email_detail.date:
				try:
					print("IN here 11")
					email_date_obj = datetime.strptime(email_detail.date, "%Y-%m-%d").date()
					print("IN here 12")
					email_detail.age_days = (today - email_date_obj).days
					print("IN here 13")
					print(f"Email date: {email_detail.date}, age: {email_detail.age_days} days")
					print("IN here 14")
				except Exception as e:
					print("IN here 15")
					print(f"Error calculating age for email date {email_detail.date}: {e}")
					print("IN here 16")
					email_detail.age_days = None
					print("IN here 17")
			print("IN here 18")
			print("What's the detail in the email: ", email_detail.dict())
			emails.append(email_detail.dict())
			print("IN here 19")
		
		# Save emails to file
		print("IN here 20")
		with open('output/fetched_emails.json', 'w') as f:
			print("IN here 21")
			json.dump(emails, f, indent=2)
			print("IN here 22")
		print("IN here 23")
		print(f"Fetched and saved {len(emails)} emails to output/fetched_emails.json")
		print("IN here 24")
		print(inputs)
		return inputs
	
	print("IN here 25")
	load_dotenv()
	print("IN here 26")
	llm = LLM(
    model=os.getenv("MODEL", "ollama/llama3.2:latest"),
    base_url=os.getenv("LITELLM_API_BASE", "http://localhost:11434"),
    api_key=os.getenv("OPENAI_API_KEY", "ollama"),  # dummy key to avoid auth errors
)


#The agents.yaml is the setup for the agents. It tells the agent what to do for it's system prompt
#The agents would have this system prompt, that it would use to perform actions.
	@agent
	def categorizer(self) -> Agent:
		"""The email categorizer agent."""
		print("IN here 27")
		return Agent(
			config=self.agents_config['categorizer'],
			tools=[FileReadTool()],  # Hmmm what does this do? How does it work? It reads the file I guess
			llm=self.llm,
		)

	@agent
	def organizer(self) -> Agent:
		"""The email organization agent."""
		print("IN here 28")
		return Agent(
			config=self.agents_config['organizer'],
			tools=[GmailOrganizeTool(), FileReadTool()], 
			llm=self.llm,
		)
		
	@agent
	def response_generator(self) -> Agent:
		"""The email response generator agent."""
		print("IN here 29")
		return Agent(
			config=self.agents_config['response_generator'],
			tools=[SaveDraftTool()],
			llm=self.llm,
		)
	
	@agent
	def notifier(self) -> Agent:
		"""The email notification agent."""
		print("IN here 29-b")
		return Agent(
			config=self.agents_config['notifier'],
			tools=[SlackNotificationTool()],
			llm=self.llm,
		)

	@agent
	def cleaner(self) -> Agent:
		"""The email cleanup agent."""
		print("IN here 30")
		return Agent(
			config=self.agents_config['cleaner'],
			tools=[GmailDeleteTool(), EmptyTrashTool()],
			llm=self.llm,
		)

######The tasks start below hereee
	@task
	def categorization_task(self) -> Task:
		"""The email categorization task."""
		print("IN here 31")
		return Task(
			config=self.tasks_config['categorization_task'],
			output_pydantic=SimpleCategorizedEmail
		)
	
	@task
	def organization_task(self) -> Task:
		"""The email organization task."""
		print("IN here 32")
		return Task(
			config=self.tasks_config['organization_task'],
			output_pydantic=OrganizedEmail,
		)

	@task
	def response_task(self) -> Task:
		"""The email response task."""
		print("IN here 33")
		return Task(
			config=self.tasks_config['response_task'],
			output_pydantic=EmailResponse,
		)
	
	@task
	def notification_task(self) -> Task:
		"""The email notification task."""
		print("IN here 34")
		return Task(
			config=self.tasks_config['notification_task'],
			output_pydantic=SlackNotification,
		)

	@task
	def cleanup_task(self) -> Task:
		"""The email cleanup task."""
		print("IN here 35")
		return Task(
			config=self.tasks_config['cleanup_task'],
			output_pydantic=EmailCleanupInfo,
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the email processing crew."""
		print("IN here 36")
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential, #Runs the tasks sequentially, basically it runs the tasks one after the other
			verbose=True
		)

	def _debug_callback(self, event_type, payload):
		"""Debug callback for crew events."""
		if event_type == "task_start":
			print("IN here 37")
			print(f"DEBUG: Starting task: {payload.get('task_name')}")
			print("IN here 38")
		elif event_type == "task_end":
			print("IN here 39")
			print(f"DEBUG: Finished task: {payload.get('task_name')}")
			print("IN here 40")
			print(f"DEBUG: Task output type: {type(payload.get('output'))}")
			print("IN here 41")
			
			# Add more detailed output inspection
			output = payload.get('output')
			if output:
				print("IN here 42")
				if isinstance(output, dict):
					print("IN here 43")
					print(f"DEBUG: Output keys: {output.keys()}")
					for key, value in output.items():
						print("IN here 44")
						print(f"DEBUG: {key}: {value[:100] if isinstance(value, str) and len(value) > 100 else value}")
				elif isinstance(output, list):
					print("IN here 45")
					print(f"DEBUG: Output list length: {len(output)}")
					if output and len(output) > 0:
						print("IN here 46")
						print(f"DEBUG: First item type: {type(output[0])}")
						if isinstance(output[0], dict):
							print("IN here 47")
							print(f"DEBUG: First item keys: {output[0].keys()}")
				else:
					print("IN here 48")
					print(f"DEBUG: Output: {str(output)[:200]}...")
		elif event_type == "agent_start":
			print("IN here 49")
			print(f"DEBUG: Agent starting: {payload.get('agent_name')}")
		elif event_type == "agent_end":
			print("IN here 50")
			print(f"DEBUG: Agent finished: {payload.get('agent_name')}")
		elif event_type == "error":
			print("IN here 51")
			print(f"DEBUG: Error: {payload.get('error')}")

	def _validate_categorization_output(self, output):
		"""Validate the categorization output before writing to file."""
		print("IN here 52")
		print(f"DEBUG: Validating categorization output: {output}")
		
		# If output is empty or invalid, provide a default
		if not output:
			print("IN here 53")
			print("WARNING: Empty categorization output, providing default")
			return {
				"email_id": "",
				"subject": "",
				"category": "",
				"priority": "",
				"required_action": ""
			}
		
		# If output is a string (which might happen if the LLM returns JSON as a string)
		if isinstance(output, str):
			print("IN here 54")
			try:
				# Try to parse it as JSON
				import json
				# First, check if the string starts with "my best complete final answer"
				print("IN here 55")
				if "my best complete final answer" in output.lower():
					# Extract the JSON part
					print("IN here 56")
					json_start = output.find("{")
					json_end = output.rfind("}") + 1
					if json_start >= 0 and json_end > json_start:
						print("IN here 57")
						json_str = output[json_start:json_end]
						print("IN here 58")
						parsed = json.loads(json_str)
						print("DEBUG: Successfully extracted and parsed JSON from answer")
						return parsed
				
				# Try to parse the whole string as JSON
				print("IN here 59")
				parsed = json.loads(output)
				print("DEBUG: Successfully parsed string output as JSON")
				return parsed
			except Exception as e:
				print(f"WARNING: Output is a string but not valid JSON: {e}")
				# Try to extract anything that looks like JSON
				import re
				json_pattern = r'\{.*\}'
				print("IN here 60")
				match = re.search(json_pattern, output, re.DOTALL)
				print("IN here 61")
				if match:
					try:
						print("IN here 62")
						json_str = match.group(0)
						parsed = json.loads(json_str)
						print("IN here 63")
						print("DEBUG: Successfully extracted and parsed JSON using regex")
						return parsed
					except:
						print("WARNING: Failed to parse extracted JSON")
		
		# If output is already a dict, make sure it has the required fields
		if isinstance(output, dict):
			print("IN here 64")
			required_fields = ["email_id", "subject", "category", "priority", "required_action"]
			missing_fields = [field for field in required_fields if field not in output]
			print("IN here 65")
			
			if missing_fields:
				print("IN here 66")
				print(f"WARNING: Output missing required fields: {missing_fields}")
				# Add missing fields with empty values
				for field in missing_fields:
					output[field] = ""
			
			# Check if the values match the expected format
			if output.get("email_id") == "12345" and output.get("subject") == "Urgent Task Update":
				print("IN here 67")
				print("WARNING: Output contains placeholder values, trying to fix")
				# Try to get the real email ID from the fetched emails
				try:
					print("IN here 68")
					with open("output/fetched_emails.json", "r") as f:
						print("IN here 69")
						fetched_emails = json.load(f)
						if fetched_emails and len(fetched_emails) > 0:
							print("IN here 70")
							real_email = fetched_emails[0]
							output["email_id"] = real_email.get("email_id", "")
							output["subject"] = real_email.get("subject", "")
				except Exception as e:
					print(f"WARNING: Failed to fix placeholder values: {e}")
		
		return output
