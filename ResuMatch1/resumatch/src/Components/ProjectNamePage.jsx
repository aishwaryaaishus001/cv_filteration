import React, { useState } from 'react';
import { Link, useNavigate, useOutletContext } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

function ProjectNamePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();


  const [pdfObject, setpdfObject] = useState([]);
  const { padding } = useOutletContext();

  const [folderName, setFolderName] = useState('No folder selected');
  const [projectTitle, setProjectTitle] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files);

    if (files.length === 0) {
      setFolderName('No folder selected');
      setpdfObject([]);
      alert('Selected folder is empty.');
      return;
    }

    const selectedFolder = files[0].webkitRelativePath.split('/')[0];
    setFolderName(selectedFolder);

    const pdfs = files.filter(file => file.type === 'application/pdf');

    if (pdfs.length === 0) {
      setpdfObject([]);
      alert('No PDF files found in the selected folder.');
      setFolderName('No folder selected');
      return;
    }

    setpdfObject(pdfs);
  };

  const { mutate, isPending } = useMutation({
    mutationFn: async (formData) => {
      const res = await axios.post("http://localhost:5001/send-pdf", formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return res.data;
    }
  });

  function send() {
    if (!pdfObject || pdfObject.length === 0) {
      alert("No Folder selected");
      console.warn("No PDF files selected");
      return;
    }

    if (!projectTitle.trim()) {
      alert("Please enter a project title.");
      return;
    }

    const formData = new FormData();
    pdfObject.forEach((file) => {
      formData.append('pdfs', file);
    });
    formData.append('projectTitle', projectTitle);

    setErrorMessage('');

    mutate(formData, {
      onSuccess: (data) => {
        console.log("Posted:", data);
        queryClient.invalidateQueries(['history-data']);
        navigate(`/new/project/home/${data.project_id}`);
      },
      onError: (error) => {
        console.error("Error posting:", error);
        const serverMessage = error?.response?.data?.error || "Something went wrong.";
        setErrorMessage(serverMessage);
      },
    });
  }

  return (
    <div className={`main-container ${padding}`}>
      {isPending && (
        <div className="loading-overlay">
          <div className="loader"></div>
          <p>Uploading PDFs and creating project...</p>
        </div>
      )}

      <div className='content'>
        <div className='contain'>   
          <Link onClick={send}>Create</Link>
        </div>

        <div className='sub-content'>
          <div className="sub-container">
            <div className="form-group">
              <label htmlFor="projectTitle">Project Title</label>
              <input
                type="text"
                id="projectTitle"
                placeholder="Enter project title"
                value={projectTitle}
                onChange={(e) => setProjectTitle(e.target.value)}
              />
              {errorMessage && (
                <div className="error-message" style={{ color: 'red', marginBottom: '1rem' }}>
                  {errorMessage}
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="selectFolder">Select Folder</label>
              <div className='button-container'>
                <button className="custom-button" onClick={() => document.getElementById('selectFolder').click()}>
                  Choose Folder
                </button>
                <input
                  type="file"
                  id="selectFolder"
                  webkitdirectory="true"
                  directory="true"
                  hidden
                  onChange={handleFileChange}
                />
                <span className="folder-name">{folderName}</span>
              </div>   
            </div>

            <div className="form-group">
              <label htmlFor="orLink">OR Link</label>
              <input type="url" id="orLink" placeholder="Enter link" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectNamePage;
