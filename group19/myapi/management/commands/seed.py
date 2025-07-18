import json
from django.core.management.base import BaseCommand
from myapi.models import User, Charity, ActivityLeader, Activity, AgeGroup, Calendar, Feedback
from leaderVoteAPI.models import ActivityLeaderVote
from django.utils import timezone

class Command(BaseCommand):
	help = 'Seeds the database with sample data'

	def handle(self, *args, **kwargs):
		Feedback.objects.all().delete()
		Calendar.objects.all().delete()
		AgeGroup.objects.all().delete()
		Activity.objects.all().delete()
		ActivityLeader.objects.all().delete()
		Charity.objects.all().delete()
		User.objects.all().delete()

		# Load data from JSON file
		with open('sample.json', 'r') as file:
			data = json.load(file)

		# Seed Users
		for user_data in data['users']:
			username = user_data['username']
			# Check if user with this username already exists
			if not User.objects.filter(username=username).exists():
				user = User.objects.create_user(
					username=username,
					password=user_data['password'],
					email=user_data['email']
				)
				if 'disabilities' in user_data:
					user.set_disabilities(user_data['disabilities'])
				user.save()
			else:
				print(f"User with username '{username}' already exists. Skipping creation.")

		# Seed Charities
# Seed Charities
		charity_objs = {}
		for charity_data in data['charities']:
			charity, created = Charity.objects.get_or_create(
				charity_name=charity_data['charity_name'],
				email=charity_data['email']
			)
			if created:
				# Set the password for the charity
				charity.set_password(charity_data['password'])
				charity.save()
				self.stdout.write(f"Charity '{charity.charity_name}' created.")
			else:
				self.stdout.write(
					f"Charity '{charity.charity_name}' already exists. Skipping creation.")

			# Use the charity name from the data as the key to ensure it matches when accessed later.
			# This assumes that the 'charity_name' in your JSON is unique and used consistently.
			charity_objs[charity_data['charity_name']] = charity

		# Seed Age Groups
		for age_group_data in data['age_groups']:
			age_group, created = AgeGroup.objects.get_or_create(
				age_range_lower=age_group_data['age_range_lower'],
				age_range_higher=age_group_data['age_range_higher'],
				group_title=age_group_data['group_title']
			)

			# If the age group was just created, print a message
			if created:
				print(f"Age Group '{age_group.group_title}' created.")

		# Seed Activities
		for activity_data in data['activities']:
			# Get the corresponding age group object
			age_group = AgeGroup.objects.get(group_title=activity_data['age_group'])
			# Get the corresponding charity object
			charity = Charity.objects.get(charity_name=activity_data['charity'])
			# Create the activity
			activity, created = Activity.objects.get_or_create(
				title = activity_data['title'],
				description=activity_data['description'],
				latitude=activity_data['latitude'],
				longitude=activity_data['longitude'],
				age_group=age_group,
				charity=charity,
				# feedback_questions=data['feedback_questions']
				feedback_questions=json.dumps(data['feedback_questions']),
				photo_file_path = activity_data['photo_file_path'],
			)


			# If the activity was just created, or if you want to update existing entries,
			# set the compatible_disabilities field.
			if created or True:  # Change or True to a condition if you only want to update sometimes
				activity.set_compatible_disabilities(
					activity_data['compatible_disabilities'])
				activity.save()

			# If the activity was just created, print a message
			if created:
				print(f"Activity '{activity.title}' created.")

		# Seed Activity Leaders
		for leader_data in data['activity_leaders']:
			# Retrieve the user associated with this leader
			# try:
			# 	user = User.objects.get(username=leader_data['user'])
			# except User.DoesNotExist:
			# 	print(f"User '{leader_data['user']}' not found. Skipping activity leader creation.")
			# 	continue

			# Retrieve the charity associated with this leader using charity_objs
			charity = charity_objs.get(leader_data['charity'])
			if charity is None:
				print(f"Charity '{leader_data['charity']}' not found. Skipping activity leader creation.")
				continue

			# Create the activity leader if they don't already exist
			activity_leader, created = ActivityLeader.objects.get_or_create(
				name= leader_data['name'],
				birth_date= leader_data['birth_date'],
				charity= charity,
				email= leader_data['email']
			)
			if created:
				print(f"Activity Leader '{leader_data['name']}' created.")
			else:
				print(f"Activity Leader '{leader_data['name']}' already exists. Skipping creation.")

		# Seed Calendar Events
		for event_data in data['calendar_events']:
			# Ensure the Activity exists
			try:
				activity = Activity.objects.get(
					title=event_data['activity_title'])
			except Activity.DoesNotExist:
				print(f"Activity '{event_data['activity_title']}' not found. Skipping calendar event creation.")
				continue
			# Ensure the ActivityLeader exists
			try:
				activity_leader = ActivityLeader.objects.get(
					name=event_data['activity_leader_name'])
			except ActivityLeader.DoesNotExist:
				print(
					f"Activity Leader '{event_data['activity_leader_name']}' not found. Skipping calendar event creation.")
				continue

			# Create the calendar event
			event, created = Calendar.objects.get_or_create(
				activity=activity,
				time=event_data['time'],
				activity_leader=activity_leader
			)

			if created:
				print(f"Calendar event for '{activity.title}' at {event.time} created.")

		# Seed Feedback
		for feedback_data in data.get('feedback_entries', []):
			# Find the user by username
			try:
				user = User.objects.get(username=feedback_data['user'])
			except User.DoesNotExist:
				print(f"User '{feedback_data['user']}' not found. Skipping feedback entry.")
				continue

			# Find the calendar event by description (this assumes you have a way to uniquely identify events by description)
			try:
				calendar_event = Calendar.objects.get(
					activity__title=feedback_data['calendar_event_title'])
			except Calendar.DoesNotExist:
				print(f"Calendar event '{feedback_data['calendar_event_title']}' not found. Skipping feedback entry.")
				continue

			# Create or update the feedback entry
			feedback, created = Feedback.objects.update_or_create(
				user=user,
				calendar_event=calendar_event,
				defaults={
					'activity_feedback_text': feedback_data.get('activity_feedback_text'),
					'leader_feedback_text': feedback_data.get('leader_feedback_text'),
					'activity_feedback_question_answers': json.dumps(feedback_data.get('activity_feedback_question_answers', '')),
				}
			)

			if created:
				print(f"Feedback for '{calendar_event.activity.title}' by '{user.username}' created.")
			else:
				print(f"Feedback for '{calendar_event.activity.title}' by '{user.username}' updated.")

		#seed leader votes
		for leader_vote in data['leader_votes']:
			try:
				user = User.objects.get(username=leader_vote['user_username'])
			except User.DoesNotExist:
				print(f"User '{leader_vote['user_username']}' not found. Skipping leader vote entry.")
				continue

			# Find the activity leader by name
			try:
				activity_leader = ActivityLeader.objects.get(name=leader_vote['leader_name'])
			except ActivityLeader.DoesNotExist:
				print(f"Activity Leader '{leader_vote['leader_name']}' not found. Skipping leader vote entry.")
				continue

			# Create the activity leader vote
			leader_vote, created = ActivityLeaderVote.objects.get_or_create(
				user=user,
				activity_leader=activity_leader,
				# You may want to adjust this based on your data
			)

			if created:
				print(f"Leader vote for '{activity_leader.name}' by '{user.username}' created.")
			else:
				print(f"Leader vote for '{activity_leader.name}' by '{user.username}' already exists.")




		self.stdout.write(self.style.SUCCESS('Database seeded successfully'))