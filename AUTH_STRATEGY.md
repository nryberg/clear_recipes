# Authentication Strategy for Clear Recipes

## Overview

This document outlines the strategy for implementing user authentication using OAuth providers (Google, GitHub) to enable users to have their own saved recipes.

## Recommended Approach

### Library: Authlib

**Why Authlib?**
- Modern, actively maintained library (Flask-OAuthlib is deprecated)
- Supports both OAuth 2.0 and OpenID Connect (OIDC)
- Works with multiple providers using the same interface
- Well-documented with Flask integration

**Alternative:** Flask-Dance is also popular and simpler for basic use cases.

### Providers

| Provider | Protocol | Use Case |
|----------|----------|----------|
| Google | OIDC (OAuth 2.0 + identity) | General users, most common |
| GitHub | OAuth 2.0 | Developer-focused users |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Clear Recipes App                       │
├─────────────────────────────────────────────────────────────┤
│  Frontend (JavaScript)                                       │
│  - Login buttons (Google, GitHub)                           │
│  - User profile display                                      │
│  - Saved recipes UI                                         │
├─────────────────────────────────────────────────────────────┤
│  Flask Backend                                               │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │  Auth Blueprint │  │ Recipe Blueprint│                   │
│  │  /auth/google   │  │ /api/recipes    │                   │
│  │  /auth/github   │  │ /api/saved      │                   │
│  │  /auth/logout   │  │                 │                   │
│  └─────────────────┘  └─────────────────┘                   │
├─────────────────────────────────────────────────────────────┤
│  Database (SQLite → PostgreSQL for production)              │
│  - users (id, email, name, provider, provider_id)           │
│  - saved_recipes (id, user_id, recipe_data, created_at)     │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Steps

### Phase 1: Setup & Database

1. **Add dependencies:**
   ```
   Authlib
   Flask-Login
   Flask-SQLAlchemy
   ```

2. **Create database models:**
   ```python
   class User(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       email = db.Column(db.String(100), unique=True)
       name = db.Column(db.String(100))
       provider = db.Column(db.String(20))  # 'google' or 'github'
       provider_id = db.Column(db.String(100))
       created_at = db.Column(db.DateTime)

   class SavedRecipe(db.Model):
       id = db.Column(db.Integer, primary_key=True)
       user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
       title = db.Column(db.String(200))
       recipe_data = db.Column(db.JSON)  # Full recipe object
       source_url = db.Column(db.String(500))
       created_at = db.Column(db.DateTime)
   ```

### Phase 2: OAuth Provider Setup

1. **Google Cloud Console:**
   - Create project at https://console.cloud.google.com
   - Enable "Google+ API" or "People API"
   - Create OAuth 2.0 credentials
   - Set authorized redirect URI: `http://localhost:5001/auth/google/callback`

2. **GitHub Developer Settings:**
   - Register app at https://github.com/settings/developers
   - Create OAuth App
   - Set callback URL: `http://localhost:5001/auth/github/callback`

### Phase 3: Flask Auth Routes

```python
# auth.py blueprint
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

# Register Google
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

# Register GitHub
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    client_kwargs={'scope': 'user:email'}
)

@auth_bp.route('/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    # Create or update user in database
    # Log user in with Flask-Login
    return redirect('/')
```

### Phase 4: Frontend Integration

1. **Add login UI to home page:**
   - "Sign in with Google" button
   - "Sign in with GitHub" button
   - Show user avatar/name when logged in

2. **Add "Save Recipe" button:**
   - Appears on recipe viewer when logged in
   - Saves current recipe to user's account

3. **Add "My Recipes" section:**
   - List of saved recipes on home page
   - Only visible when logged in

## Environment Variables

```bash
# .env file (DO NOT COMMIT)
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx
GITHUB_CLIENT_ID=xxx
GITHUB_CLIENT_SECRET=xxx
DATABASE_URL=sqlite:///recipes.db
```

## Security Considerations

1. **Session Management:**
   - Use secure, HTTP-only cookies
   - Set appropriate session timeout
   - Use `app.secret_key` from environment variable

2. **CSRF Protection:**
   - Authlib handles OAuth state parameter
   - Consider Flask-WTF for form submissions

3. **Data Privacy:**
   - Only store necessary user info (email, name)
   - Allow users to delete their account/data
   - Clear privacy policy

## Migration Path

1. **Start with local development:** SQLite database
2. **Production:** Migrate to PostgreSQL (Heroku, Railway, etc.)
3. **Scaling:** Consider Redis for session storage

## Timeline Estimate

| Phase | Description | Complexity |
|-------|-------------|------------|
| 1 | Database setup & models | Low |
| 2 | OAuth provider registration | Low (external setup) |
| 3 | Auth routes & Flask-Login | Medium |
| 4 | Frontend login UI | Medium |
| 5 | Save recipe functionality | Low |
| 6 | My recipes page | Low |

## Resources

- [Authlib Documentation](https://docs.authlib.org/en/latest/client/flask.html)
- [Miguel Grinberg's OAuth Tutorial](https://blog.miguelgrinberg.com/post/oauth-authentication-with-flask-in-2023)
- [Real Python Flask Google Login](https://realpython.com/flask-google-login/)
- [Google Cloud Console](https://console.cloud.google.com)
- [GitHub Developer Settings](https://github.com/settings/developers)

## Next Steps

1. Review this strategy document
2. Set up Google Cloud and GitHub OAuth apps
3. Implement Phase 1 (database models)
4. Implement authentication routes
5. Add frontend login UI
6. Implement save recipe feature
