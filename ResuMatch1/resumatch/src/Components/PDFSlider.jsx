import React, { useRef, useState, useEffect } from "react";
import { Link, useOutletContext, useParams } from "react-router-dom";
import PDFView from "./PDFView";
import filter from '../assets/filter.svg';
import view from '../assets/view.svg';
import explain from '../assets/explain.svg';
import ProfileRadarChart from './ProfileRadarChart';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

function PDFSlider() {
  const list = ['All', 'Skill', 'Education', 'Experience', 'Projects', 'Certification'];
  const categoryKeyMap = {
    1: "skill",
    2: "education",
    3: "experience",
    4: "projects",
    5: "certification"
  };

  const { projectId } = useParams();
  const { padding } = useOutletContext();
  const carouselRef = useRef(null);
  const dropdownRef = useRef(null);

  const [visibility, setVisibility] = useState(false);
  const [listItem, setListItem] = useState(0);
  const [selectedPDFIndex, setSelectedPDFIndex] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [rankedCandidates, setRankedCandidates] = useState([]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setVisibility(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Fetch ranked candidates from backend
  const fetchRankedCandidates = async () => {
    const response = await axios.get("http://localhost:5001/rank-resumes", {
      params: { project_id: projectId }
    });
    return response.data.ranked;
  };

  const { data: rankedData = [], isLoading, isError, error } = useQuery({
    queryKey: ['ranked-candidates', projectId],
    queryFn: fetchRankedCandidates,
  });

  useEffect(() => {
    if (rankedData && rankedData.length > 0) {
      const transformed = rankedData.map(candidate => ({
        name: candidate.name || "N/A",
        file_path: candidate.file_path,
        totalScore: candidate.result?.TotalScore || 0,
        summary: candidate?.summary || "No summary available.",
        skill: {
          score: candidate.result?.Skills?.Score || 0,
          match: candidate.result?.Skills?.Matches || []
        },
        education: {
          score: candidate.result?.Education?.Score || 0,
          match: candidate.result?.Education?.Matches || []
        },
        experience: {
          score: candidate.result?.Experience?.Score || 0,
          match: candidate.result?.Experience?.Matches || []
        },
        projects: {
          score: candidate.result?.Projects?.Score || 0,
          match: candidate.result?.Projects?.Matches || []
        },
        certification: {
          score: candidate.result?.Certifications?.Score || 0,
          match: candidate.result?.Certifications?.Matches || []
        }
      }));


      setRankedCandidates(transformed);
    }
  }, [rankedData]);


  const scroll = (direction) => {
    const scrollAmount = carouselRef.current.offsetWidth / 3 + 2;
    carouselRef.current.scrollBy({
      left: direction === 'next' ? scrollAmount : -scrollAmount,
      behavior: 'smooth'
    });
  };

  const openPDF = (url) => {
    window.open(url, "_blank");
  };

  const sortedData = [...rankedCandidates].sort((a, b) => {
    if (listItem === 0) return b.totalScore - a.totalScore;
    const key = categoryKeyMap[listItem];
    return b[key]?.score - a[key]?.score;
  });

  const selected = sortedData[selectedPDFIndex];

  const radarProfileData = selected ? {
    chart: [
      { subject: "Skills", value: selected.skill?.score || 0 },
      { subject: "Education", value: selected.education?.score || 0 },
      { subject: "Projects", value: selected.projects?.score || 0 },
      { subject: "Experience", value: selected.experience?.score || 0 },
      { subject: "Certification", value: selected.certification?.score || 0 }
    ],
    summary: selected.summary || "No summary available."
  } : null;


  if (isLoading) return <p>Loading ranked candidates...</p>;
  if (isError) return <p>Error loading ranked candidates: {error.message}</p>;

  console.log("Ranked Candidates Data:", rankedData);
  console.log("Sorted Data:", sortedData);
  console.log("Radar Data:", radarProfileData);

  return (
    <div className={`main-container ${padding}`}>
      <div className="content">
        <div className="contain flex-container">
          <Link to="#"><img src={filter} alt="filter" /></Link>

          <div className="drop-down" ref={dropdownRef} onClick={() => setVisibility(!visibility)}>
            <span>{list[listItem]} ▼</span>
            <div className={`drop-down-options ${visibility ? 'visible' : 'in-visible'}`}>
              <ul>
                {list.map((item, index) => (
                  <li key={index} onClick={() => setListItem(index)}>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
                <div className="sub-content">
                  <div className="sub-container">
                    <div className="carousel-container">
                      <button className="prev-next-button" id="prevBtn" onClick={() => scroll('prev')}>&#10094;</button>
                      <div className="carousel" ref={carouselRef}>
                         {sortedData.map((candidate, index) => (
                          <div key={index} className="item">
                            <div className="number">
                              <span className="number-cover">{index+1}</span>
                            </div>
                            <div className="view-container">
                              <div className="view-icon" onClick={() => openPDF(candidate.file_path)}>
                                <img src={view} alt="view" />
                              </div>
        
                              <div className="explain-icon" onClick={() => { setSelectedPDFIndex(index); setIsModalOpen(true); }}>
                                <img src={explain} alt="explain" />
                              </div>
        
                              <PDFView file={candidate.file_path} />
                            </div>
                          </div>
                        ))}
                      </div>
                      <button className="prev-next-button" id="nextBtn" onClick={() => scroll('next')}>&#10095;</button>
                    </div>
                  </div>
                </div>
      </div>

      {isModalOpen && radarProfileData && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>OVERVIEW</h2>
            <ProfileRadarChart data={radarProfileData.chart} />

            <h2>SUMMARY</h2>
            <p>{radarProfileData.summary}</p>

            <div className="modal-close" onClick={() => setIsModalOpen(false)}>✕</div>
          </div>
        </div>
      )}

    </div>
  );
}

export default PDFSlider;
