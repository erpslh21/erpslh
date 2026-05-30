# App Branding Generalization Plan: Transitioning from SLH-OP to SK-OP

This document provides a comprehensive blueprint to centralize the application branding across the codebase. By decoupling the app name from hardcoded templates, routes, and client-side resources, we prepare the system to be easily rebranded (from `SLH-OP` to `SK-OP`) and fully generic for future mass distribution.

---

## 1. Inventory of Current Hardcoded Branding Occurrences

A search across the codebase reveals that the name `SLH-OP` or `SLH` is currently utilized in multiple independent layers:

### 1.1 Configuration Files
- **`config.py`**:
  ```python
  APP_NAME = "SLH-OP (DEV)"
  # and
  APP_NAME = "SLH-OP"
  ```

### 1.2 Python Routes (Hardcoded Titles)
Several backend views hardcode the `SLH-OP:` prefix inside route titles passed to templates:
- **`app/routes/admin.py`**: `title = "SLH-OP: [TEST] Mortality"`, `title = "SLH-OP: [TEST] Weight"`
- **`app/routes/health.py`**: `title = "SLH-OP: Weight Entry"`, `title = "SLH-OP: Grading Report"`, `title = "SLH-OP: Post Mortem"`

### 1.3 Jinja Templates
Branding text is hardcoded inside HTML page titles, logos, and scripts:
- **`app/templates/base_tabler.html`**:
  - `window.SLHConfig` configuration object.
  - Svg classes: `.slh-logo`, `.slh-logo-circle`, `.slh-logo-graphic`, `.slh-eye`.
  - Offline local storage keys: `slh_offline_user_id`, `slh_offline_user_role`, `slh_offline_user_dept`.
- **`app/templates/bodyweight.html`**: `<title>Weight Grading - SLH Dashboard</title>`
- **`app/templates/broiler/broiler_new_flock.html`**: Placeholder text `"e.g. SLH Hatchery Batch A"`.
- **`app/templates/daily_log_form.html`**: `slh_form_layout_mode` and local draft draft storage key `slh_draft_{houseId}_{dateVal}`.
- **`app/templates/admin/project_report.html`**: Project Value Report titles and system descriptions.

### 1.4 PWA Manifests
- **`app/static/manifest.json`** & **`manifest_dev.json`**: Hardcoded `"name": "SLH-OP"`, `"short_name": "SLH-OP"`.

---

## 2. Dynamic Centralization Blueprint

To decouple the branding, we must establish a **Single Source of Truth** for the application name utilizing Flask’s configuration system.

### 2.1 Backend Route Updates
Instead of hardcoding title prefixes in controller route variables, routes should query the current application context.

*Before:*
```python
title = "SLH-OP: Post Mortem"
```

*After:*
```python
from flask import current_app
title = f"{current_app.config.get('APP_NAME', 'SK-OP')}: Post Mortem"
```

### 2.2 Global Context Processor
To avoid manually passing `app_name` to every single `render_template()` call, we register a global Jinja2 context processor in the Flask application factory (`app/__init__.py`):

```python
@app.context_processor
def inject_global_branding():
    return dict(
        app_name=current_app.config.get("APP_NAME", "SK-OP"),
        app_short_name=current_app.config.get("APP_SHORT_NAME", "SK-OP")
    )
```

This injects `{{ app_name }}` and `{{ app_short_name }}` into **all** rendered HTML templates globally.

### 2.3 Template Refactoring
Refactor template titles and general branding:

*Before:*
```html
<title>{% block title %}Weight Grading - SLH Dashboard{% endblock %}</title>
```

*After:*
```html
<title>{% block title %}Weight Grading - {{ app_short_name }} Dashboard{% endblock %}</title>
```

---

## 3. Generalizing PWA & Client-Side Assets

To allow full white-label capabilities, client-side offline keys, manifest files, and local databases must also be decoupled.

### 3.1 Dynamic Manifest Resolution
Instead of serving a static JSON file, we can serve the PWA manifest dynamically through a Flask route. This allows the manifest to pull directly from the active configuration:

```python
@app.route('/manifest.json')
def dynamic_manifest():
    app_name = current_app.config.get("APP_NAME", "SK-OP")
    app_short_name = current_app.config.get("APP_SHORT_NAME", "SK-OP")
    
    manifest_data = {
        "name": app_name,
        "short_name": app_short_name,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#ffffff",
        "theme_color": "#18496a",
        "icons": [
            {
                "src": "/static/assets/icon-192.png",
                "sizes": "192x192",
                "type": "image/png"
            },
            {
                "src": "/static/assets/icon-512.png",
                "sizes": "512x512",
                "type": "image/png"
            }
        ]
    }
    return jsonify(manifest_data)
```

### 3.2 Standardizing LocalStorage Prefix
Rename client-side prefixes to use a generic config value dynamically generated in the layout or standard lowercase namespaces:

*Before:*
```javascript
localStorage.setItem("slh_offline_user_id", userId);
```

*After:*
```javascript
localStorage.setItem("app_offline_user_id", userId);
```

---

## 4. Rebranding Checklist: SLH-OP to SK-OP

Once the codebase has been centralized, changing the name to `SK-OP` or a different generic branding requires only a single modification inside `config.py`:

```python
class Config:
    APP_NAME = "SK-OP"
    APP_SHORT_NAME = "SK-OP"
```

### Step-by-Step Rebranding Migration Guide:
1. **Config Modification**: Update `APP_NAME` in `config.py` to `"SK-OP"`.
2. **Dynamic Context processor Integration**: Setup the context processor in the Flask app creation factory.
3. **Template Title Replacements**: Replace hardcoded `SLH-OP` occurrences in HTML files to `{{ app_name }}`.
4. **Route Title Replacements**: Replace static `title = "SLH-OP: ..."` in `app/routes/admin.py` and `app/routes/health.py` with `current_app.config['APP_NAME']`.
5. **Static File Updates**: Rename static assets or graphics with the generic `.app-logo` class name instead of `.slh-logo`.
