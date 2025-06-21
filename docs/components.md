# Components

An observation page that should include 3 components such as matrix cards,
performances graph, and data table.

**File Structure**:

```text
- auth
    - models/
    - schemas/
    - templates/
    - crud.py
    - deps.py
    - routes.py
    - securities.py
    - views.py
- routes/
    - workflow/
        - templates/        <-- Jinja templates
        - crud.py           <-- Operation between Schema & Model
        - routes.py         <-- API
        - schemas.py        <-- Schema interface
        - views.py          <-- UI with Jinja template
    - profile/
        - templates/
        - ...
    - models.py
```
