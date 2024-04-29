from django.urls import path

from .views import (PostListView, UserSearch, AddLikes, AddDisLike, RemoveFollower, AddFollower, ProfileEditView,
                    PostDetailView,
                    PostEditView, Explore, SharedPostView, ThreadNotification, ListThreads, ThreadView, CreateThread,
                    RemoveNotification,
                    PostNotification,
                    FollowNotification, AddCommentLikes, CreateMessage, AddCommentDisLike, ListFollowers,
                    PostDeleteView, CommentReplyView,
                    CommentDeleteView,
                    ProfileView)

urlpatterns = [

    path('', PostListView.as_view(), name='post-list'),
    path('explore/', Explore.as_view(), name='explore'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:post_pk>/comment/<int:pk>/like', AddCommentLikes.as_view(), name='comment-likes'),
    path('post/<int:post_pk>/comment/<int:pk>/dislike', AddCommentDisLike.as_view(), name='comment-dislikes'),
    path('post/<int:post_pk>/comment/<int:pk>/reply', CommentReplyView.as_view(), name='comment-reply'),
    path('post/<int:pk>/like', AddLikes.as_view(), name='like'),
    path('post/<int:pk>/dislike', AddDisLike.as_view(), name='dislike'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/', ListFollowers.as_view(), name='list-followers'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),
    path('search/', UserSearch.as_view(), name='profile-search'),
    path('notification/<int:notification_pk>/post/<int:post_pk>', PostNotification.as_view(), name='post-notification'),
    path('notification/<int:notification_pk>/profile/<int:profile_pk>', FollowNotification.as_view(),
         name='follow-notification'),
    path('notification/delete/<int:notification_pk>', RemoveNotification.as_view(), name='notification-delete'),
    path('inbox/', ListThreads.as_view(), name='inbox'),
    path('inbox/create-thread', CreateThread.as_view(), name='create-thread'),
    path('inbox/<int:pk>/', ThreadView.as_view(), name='thread'),
    path('inbox/<int:pk>/create-message/', CreateMessage.as_view(), name='create-message'),
    path('notification/<int:notification_pk>/thread/<int:object_pk>', ThreadNotification.as_view(),
         name='thread-notification'),

    path('post/<int:pk>/share', SharedPostView.as_view(), name='share-post')

]
