# Launch Factory v2

Launch Factory builds a local review package from a release folder.

The package includes a captioned social video, a blog post, five email variants, a changelog, a login animation, and an in-app popup.

Every copy block cites claim IDs, and each claim has an exact quote from a local source file.

The campaign plan covers two weeks across email, blog, changelog, popup, login, LinkedIn, X, Threads, Instagram, and TikTok.

A person reviews claims before a normal build. Finished assets still need human review. Nothing publishes, sends, or schedules.

The build uses Python and FFmpeg locally. The AI agent writes the drafts in its host; the command line validates and renders them.

A changed source invalidates its Claims Lock. The builder refuses to overwrite an existing package.
