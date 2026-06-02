def create_comment(form, task, author):
    comment = form.save(commit=False)
    comment.task = task
    comment.author = author
    comment.save()
    return comment
