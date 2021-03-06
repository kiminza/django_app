from django.shortcuts import render, get_object_or_404, redirect
# from django.core.urlresolvers import reverse_lazy ,,deprecated for django2+
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.decorators import login_required

from blog.models import Post
from blog.forms import MailForm


# the context arg of render is optional
@login_required
def home(request):
    context = {"posts": Post.objects.all(), }
    return render(request, "blog/home.html", context)


class PostListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = "blog/home.html"  # app/<model>_<view_type>.html
    context_object_name = "posts"
    ordering = ['-date_posted']
    paginate_by = 5


class UserPostListView(ListView, LoginRequiredMixin):
    model = Post
    template_name = "blog/user_post.html"  # app/<model>_<view_type>.html
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get("username"))
        return Post.objects.filter(author=user).order_by("-date_posted")


class PostDetailView(DetailView, LoginRequiredMixin):  # accepts a pk or slug but not id
    model = Post
    template_name = "blog/post_detail.html"  # app/<model>_<view_type>.html
    # context_object_name="posts"


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def test_func(self):  # preventing another user from updating other users post
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


class PostDeleteView(DeleteView, LoginRequiredMixin):  # accepts a pk or slug but not id
    model = Post
    success_url = reverse_lazy('blog_home')
    # template_name = "blog/post_detail.html"

    def test_func(self):  # preventing another user from updating other users post
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False


@login_required
def sendmail(request):
    if request.method == "POST":
        form = MailForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.sender = User.objects.get(id=request.user.id).email
            instance.save()
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')
            sender = form.cleaned_data.get('sender')
            to = [form.cleaned_data.get('to')]
            send_mail(subject, message, sender, to)
            messages.success(request, "Your email has been successfully sent!")
            return redirect('blog_home')
    else:
        form = MailForm()
    return render(request, 'blog/mail.html', {'form': form})


def about(request):
    return render(request, "blog/about.html", {"title": "About"})
