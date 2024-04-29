from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic.edit import UpdateView, DeleteView

from .forms import PostForm, CommentForm, ThreadForm, MessageForm, ShareForm, ExploreForm
from .models import Post, Comment, UserProfile, Notification, ThreadModel, MessageModel, Tag


# Create your views here.

class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user

        posts = Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]
        )
        form = PostForm()

        share_form = ShareForm()

        context = {
            'post_list': posts,
            'form': form,
            'shareform': share_form,
        }
        return render(request, 'socialApp/post_list.html', context)

    def post(self, request, *args, **kwargs):

        logged_in_user = request.user

        posts = Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]
        )

        share_form = ShareForm()

        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                new_post = form.save(commit=False)
                new_post.author = logged_in_user
                new_post.save()

                new_post.create_tags()

                # Handling multiple image files
                # files = request.FILES.getlist('image')
                #
                # for f in files:
                #     img = Image.objects.create(image=f)
                #     img.save()
                #     new_post.image.add(img)
                # new_post.save()
            return redirect('post-list')

        else:
            form = PostForm()

        # form = PostForm(request.POST, request.FILES)
        # files = request.FILES.getlist('image')
        #
        # if form.is_valid():
        #     new_post = form.save(commit=False)
        #     new_post.author = request.user
        #     new_post.save()
        #
        #     for f in files:
        #         img = Image(image=f)
        #         new_post.image.add(img)
        #
        #     new_post.save()

        context = {
            'post_list': posts,
            'form': form,
            'shareform': share_form
        }

        return render(request, 'socialApp/post_list.html', context)


class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()

        comments = Comment.objects.filter(post=post.pk)
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        return render(request, 'socialApp/post_detail.html', context)

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()  # Create a new instance of the comment form
        if request.method == 'POST':
            form = CommentForm(request.POST)
            if form.is_valid():
                new_comment = form.save(commit=False)
                new_comment.author = request.user
                new_comment.post = post
                new_comment.save()

                new_comment.create_tags()

                return redirect('post-detail', pk=post.pk)  # Use pk instead of post.id

        comments = Comment.objects.filter(post=post.pk)

        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author,
                                                   post=post)

        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        return render(request, 'socialApp/post_detail.html', context)


class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)

        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()

        notification = Notification.objects.create(notification_type=2, from_user=request.user,
                                                   to_user=parent_comment.author, comment=new_comment)
        return redirect('post-detail', pk=post_pk)


class PostEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['body']
    template_name = 'socialApp/post_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'socialApp/post_delete.html'
    success_url = reverse_lazy('post-list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'socialApp/comment_delete.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):

        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user)

        followers = profile.followers.all()

        if len(followers) == 0:
            is_following = False

        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False

        number_of_followers = len(followers)

        context = {
            'user': user,
            'profile': profile,
            'posts': posts,
            'number_of_followers': number_of_followers,
            'is_following': is_following,

        }
        return render(request, 'socialApp/user_profile.html', context)


class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['name', 'bio', 'birth_date', 'location', 'picture']
    template_name = 'socialApp/user_profile_edit.html'

    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('profile', kwargs={'pk': pk})

    def test_func(self):
        profile = self.get_object()
        return self.request.user == profile.user


class AddFollower(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.add(request.user)
        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)

        return redirect('profile', pk=profile.pk)


class RemoveFollower(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        profile.followers.remove(request.user)

        return redirect('profile', pk=profile.pk)


class AddLikes(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        # for check dislike

        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            post.dislikes.remove(request.user)
        # for check likes
        is_like = False

        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author,
                                                       post=post)

        if is_like:
            post.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddDisLike(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)

        # for if likes
        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)

        # for dislikes
        is_dislike = False

        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            post.dislikes.add(request.user)

        if is_dislike:
            post.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddCommentLikes(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        # for check dislike

        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break

        if is_dislike:
            comment.dislikes.remove(request.user)
        # for check likes
        is_like = False

        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=2, from_user=request.user,
                                                       to_user=comment.author, comment=comment)

        if is_like:
            comment.likes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class AddCommentDisLike(LoginRequiredMixin, View):

    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)

        # for if likes
        is_like = False
        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            comment.likes.remove(request.user)

        # for dislikes
        is_dislike = False

        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            comment.dislikes.add(request.user)

        if is_dislike:
            comment.dislikes.remove(request.user)

        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)


class SharedPostView(View):

    def post(self, request, pk, *args, **kwargs):
        original_post = Post.objects.get(pk=pk)
        form = ShareForm(request.POST)

        if form.is_valid():
            new_post = Post(
                shared_body=self.request.POST.get('body'),
                body=original_post.body,
                author=original_post.author,
                created_on=original_post.created_on,
                shared_user=request.user,
                shared_on=timezone.now(),
            )
            new_post.save()

            for img in original_post.image.all():
                new_post.image.add(img)
            new_post.save()

        return redirect('post-list')


class UserSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )

        context = {
            'profile_list': profile_list,
        }

        return render(request, 'socialApp/search.html', context)


class ListFollowers(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()

        context = {
            'profile': profile,
            'followers': followers,
        }
        return render(request, 'socialApp/followers_list.html', context)


class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)

        notification.user_has_seen = True
        notification.save()
        return redirect('post-detail', pk=post_pk)


class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = UserProfile.objects.get(pk=profile_pk)

        notification.user_has_seen = True
        notification.save()
        return redirect('profile', pk=profile_pk)


class ThreadNotification(View):

    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        thread = ThreadModel.objects.get(pk=object_pk)

        notification.user_has_seen = True
        notification.save()

        return redirect('thread', pk=object_pk)


class RemoveNotification(View):

    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)

        notification.user_has_seen = True
        notification.save()

        return HttpResponse('success', content_type='text/plain')


class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))

        context = {
            'threads': threads
        }
        return render(request, 'socialApp/inbox.html', context)


class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()

        context = {
            'form': form,
        }
        return render(request, 'socialApp/create_thread.html', context)

    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)

        username = request.POST.get('username')

        try:
            receiver = User.objects.get(username=username)

            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists() or ThreadModel.objects.filter(
                    user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('thread', pk=thread.pk)

            elif ThreadModel.objects.filter(user=receiver, receiver=request.user).exists():
                thread = ThreadModel.objects.filter(user=receiver, receiver=request.user)[0]
                return redirect('thread', pk=thread.pk)

            if form.is_valid():
                thread = ThreadModel(
                    user=request.user,
                    receiver=receiver
                )
                thread.save()

                return redirect('thread', pk=thread.pk)

        except:
            messages.error(request, 'Invalid Username')
            return redirect('create-thread')


class ThreadView(View):

    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread = ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)

        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }

        return render(request, 'socialApp/thread.html', context)


class CreateMessage(View):

    def post(self, request, pk, *args, **kwargs):

        form = MessageForm(request.POST, request.FILES)

        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user

        else:
            receiver = thread.receiver

        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender_user = request.user
            message.receiver_user = receiver
            message.save()

        notification = Notification.objects.create(
            notification_type=4,
            from_user=request.user,
            to_user=receiver,
            thread=thread
        )

        return redirect('thread', pk=pk)


class Explore(View):

    def get(self, request, *args, **kwargs):
        explore_form = ExploreForm()
        query = self.request.GET.get('query')
        tag = Tag.objects.filter(name=query).first()

        if tag:
            posts = Postobjects.filter(tags__in=[tag])

        else:
            posts = Post.objects.all()

        context = {
            'tag': tag,
            'posts': posts,
            'explore_form': explore_form,
        }

        return render(request, 'socialApp/explore.html', context)

    def post(self, request, *args, **kwargs):

        explore_form = ExploreForm(request.POST)

        if explore_form.is_valid():
            query = explore_form.cleaned_data['query', None]
            tag = Tag.objects.filter(name=query).first()

            posts = None

            if tags:
                posts = Post.objects.filter(tags__in=[tag])

            if posts:
                context = {
                    'tag': tag,
                    'posts': posts,
                }
            else:
                context = {
                    'tag': tag,
                }
            return HttpResponse(f'/socialmediaApp/explore?query={query}')

        return redirect('/socialmediaApp/explore')
