# Components

**File structure of this application**:

```text
- models
- routes
    - page
        - templates/        <-- Jinja templates
        - crud.py           <-- Operation between Schema & Model
        - models.py         <-- Model interface
        - routes.py         <-- API
        - schemas.py        <-- Schema interface
        - views.py          <-- UI with Jinja template
```

## Home

The home page will contain all alert matrix.

## Routes

An observation page that should include 3 components such as matrix cards,
performances graph, and data table.

### Workflows

- Active workflow
- Failed workflow

- Data Table
  - Workflow name
  - Workflow description

### Schedules

### Audits

- Search template
- Audits table
  - workflow name
  - release id

### Logs

- Search template
- Logs table
  - running ID
  - create date
  - logs location

## Setting

### Admin

- Group Management
- User Management
  - Create/Delete/Update User
- Role Management
  - Create/Delete/Update Role
- Policy Management

### User

- Profile setting
  - Change name
  - Change password
  - Change email
