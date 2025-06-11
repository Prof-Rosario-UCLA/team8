# Main Frontend

Home page is under `web/src/app/page.tsx`

# Auth Middleware

On protected routes, we wrap the base layout for those directories (since we're using App Router) with the AuthProvider middleware which first checks for user auth by fetching from a protected endpoint before allowing the content to appear.

`web/src/auth/AuthProvider.tsx`

# ShadCN Components + Acccessibility + Tailwind 

We use components from the ShadCN component library for easy to use primitives and out the box accessibility support due to their inclusion of aria labels and tab focus. We still do further styling with Tailwind to maintain our site's consistent theming.

Beyond these two main accessibility features, we support alt text on images for screen readers and in general the site has a quite high lighthouse score for accessibility even on the editor pages.

# Editor Page

We make use of a React drag and drop librbary to support drag and drop in the table of contents (the TOC component) and propagate those changes with callbacks to reorder the underlying data. We also have a editor that has saving functionality, AI rating, geolocation, form validation, datepicking via calendar ui, and compiling via our compiler microservice, and downloading the final pdf from the google storage bucket.

# Dashboard

We use a dashboard to show all of the resumes and allow for creation. This is our main menu and portal to access resumes.

# Responsiveness + Mobile + SPA

All our layouts are responsive and will switch to adapt to smaller screen resolutions down to 320 px.
We for example in the editor hide the table of contents on mobile screens and switch from the two panel side by side view into a tab based view.

The dashboard likewise changes to flex column to adapt.

All of our layouts are designed to fit within the viewport for SPA requirements, when there are longer views like the editor form only that section will scroll without the whole page scrolling. Likewise, for our resume preview and TOC.

Our navbar collapses into icons without the labels when shrinking as well.

# Browser API Integration

We use the geolocation API from the browser to allow the user quickly to fill their current address.

We also support drag and drop on the table of contents but geolocation is our browser API use for satisfying the requirement.

# CI / CD

We use Github Actions to orchestrate CI/CD. For CI when pushing to the web directory we run a linter on CI to check for unused variables, any typing, etc and Cloud Build and App Engine for building and deployment.

# Service Workers

We use Serwist to handle service workers that cache static assets, and the results of some api calls to support partial functionality even when offline and the user will be notified that their requests will be processed once back online.

In the meanwhile, the user may continue navigating and making edits to their resume and view the cached version of the site.

We have a manifest and support PWA as well. 