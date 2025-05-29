import React, { useState, useEffect } from "react";
import { pdfjs } from "react-pdf";
import "pdfjs-dist/build/pdf.worker.min.mjs";  

// ✅ Set the correct worker path
pdfjs.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

function PDFView({ file }) {
    const [imageSrc, setImageSrc] = useState(null);

    useEffect(() => {
        const renderPDFtoImage = async () => {
            try {
                const loadingTask = pdfjs.getDocument(file);
                const pdf = await loadingTask.promise;
                const page = await pdf.getPage(1);

                const scale = 1; // Adjust for better resolution
                const viewport = page.getViewport({ scale });

                const canvas = document.createElement("canvas");
                const context = canvas.getContext("2d");
                canvas.width = viewport.width;
                canvas.height = viewport.height;

                const renderContext = { canvasContext: context, viewport };
                await page.render(renderContext).promise;

                setImageSrc(canvas.toDataURL("image/png")); // Convert canvas to image
            } catch (error) {
                console.error("❌ PDF Load Error:", error);
            }
        };

        renderPDFtoImage();
    }, [file]);

    return (
        <>
            {imageSrc ? (
                <img src={imageSrc} alt="PDF Preview" style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "10px" }} />
            ) : (
                <p>Loading PDF...</p>
            )}
        </>
    );
}

export default PDFView;


// // RankedResultsList.jsx
// import React, { useEffect, useState } from "react";
// import RankedCandidateCard from "./RankedCandidateCard";

// function RankedResultsList({ projectId }) {
//     const [rankedData, setRankedData] = useState([]);
//     const [loading, setLoading] = useState(true);

//     useEffect(() => {
//         const fetchRankings = async () => {
//             try {
//                 const response = await fetch(`http://localhost:5001/rank-resumes?project_id=${projectId}`);
//                 const data = await response.json();
//                 if (data.ranked) {
//                     setRankedData(data.ranked);
//                 }
//             } catch (error) {
//                 console.error("Error fetching rankings:", error);
//             } finally {
//                 setLoading(false);
//             }
//         };

//         fetchRankings();
//     }, [projectId]);

//     if (loading) return <p>Loading ranked candidates...</p>;
//     if (rankedData.length === 0) return <p>No rankings available.</p>;

//     return (
//         <div>
//             <h2>Ranked Candidates</h2>
//             {rankedData.map((candidate, index) => {
//                 // You’ll need logic to match PDFs to names if not 1:1
//                 const pdfUrl = `http://localhost:5001/uploads/${encodeURIComponent(candidate.name)}.pdf`;
//                 return (
//                     <RankedCandidateCard
//                         key={index}
//                         candidate={candidate}
//                         pdfUrl={pdfUrl}
//                     />
//                 );
//             })}
//         </div>
//     );
// }

// export default RankedResultsList;
