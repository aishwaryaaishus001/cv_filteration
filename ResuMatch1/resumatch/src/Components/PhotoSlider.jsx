import React, { useRef } from 'react'
import { useOutletContext } from 'react-router-dom'
import PDFView from './PDFView';

function PhotoSlider() {
    const { padding } = useOutletContext()

    const carouselRef = useRef(null);

    const scroll = (direction) => {
        const scrollAmount = carouselRef.current.offsetWidth / 3; // Each item is 1/3 of the container width
        if (direction === 'next') {
        carouselRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
        } else {
        carouselRef.current.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
        }
    };

  return (

        <div className={`main-container ${padding}`}>
            <div className='content'>
                <div className="carousel-container">
                    <button className="prev-next-button" id="prevBtn" onClick={() => scroll('prev')}>&#10094;</button>
                    <div className="carousel" ref={carouselRef}>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                        <div className="item"><PDFView file="/maneesh.pdf" /></div>
                    </div>
                    <button className="prev-next-button" id="nextBtn" onClick={() => scroll('next')}>&#10095;</button>
                </div>

            </div>
        </div>
  )
}

export default PhotoSlider