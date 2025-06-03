import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { RouterProvider, createBrowserRouter } from 'react-router-dom';
import CreateProjectPage from './Components/CreateProjectPage.jsx';
import ProjectNamePage from './Components/ProjectNamePage.jsx';
import JobDiscripPage from './Components/JobDiscripPage.jsx';
import PriorityPage from './Components/PriorityPage.jsx';
import PDFSlider from './Components/PDFSlider.jsx';
import PhotoSlider from './Components/photoSlider.jsx';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

const router = createBrowserRouter([
  {
      path: "/",
      element: <App/>,
      children: [
        {
          path: "",
          element: <CreateProjectPage />
        },
        {
          path: "/new/project",
          element: <ProjectNamePage />
        },
        {
          path: "/new/project/home/:projectId",
          element: <JobDiscripPage />
        },
        {
          path: "/new/project/priority/:projectId/:promptId",
          element: <PriorityPage />
        },
        {
          path: "/new/project/profile/:projectId/:promptId",
          element: <PDFSlider />
        },
        {
          path: "/new/project/profile/ooo",
          element: <PhotoSlider />
        }
      ]
  }
]);


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} />
    </QueryClientProvider>
  </StrictMode>
)
