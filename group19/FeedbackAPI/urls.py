from django.urls import path

from . import views

urlpatterns = [
    path('<int:activity_id>/overview', views.FeedbackOverview.as_view(), name='feedback_overview'),
    path('<int:activity_id>/activity-feedback-list/', views.ActivityFeedbackList.as_view(),
         name='activity_feedback_list'),
    path('<int:activity_id>/leader-feedback-list/', views.LeaderFeedbackList.as_view(),
         name='leader_feedback_list'),
    path('<int:event_id>/feedback-submission', views.FeedbackSubmission.as_view(),
         name='feedback_submission'),
    path('<int:event_id>/feedback-questions-list', views.FeedbackQuestions.as_view(),
         name='feedback_questions'),

    # more data
    path('<int:event_id>/feedback-questions-details', views.FeedbackQuestionDetails.as_view(),
         name='feedback_question_detail'),
]
