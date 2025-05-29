import { useEffect, useState } from 'react'
import './App.css'
import logo from './assets/logo3.svg';
import sideBArW from './assets/sidebar.svg';
import sideBArB from './assets/sidebarB.svg';
import searchIcon from './assets/search.svg';
import createIcon from './assets/createicon.svg';
import {Outlet, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios';

function App() {

  const [isIN, setisIN] = useState(true)
  const [imageSrc, setImageSrc] = useState(sideBArW); // Default image
  const [hoverSrc, sethoverSrc] = useState('show-bthB'); // Default hover
  const [padding, setPadding] = useState('main-container-padding-248'); // Default padding
  const [width, setWidth] = useState('width-85'); // Default width
  const [activeIndex, setActiveIndex] = useState(); 

  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isIN) {
        setTimeout(() => {
            setImageSrc(sideBArB); // Switch to sideBArB after delay
            sethoverSrc('show-bthW')
            setPadding('main-container-padding-0')
            setWidth('width-80')
        }, 100); 
    } else {
        setImageSrc(sideBArW); // Immediately switch back
        sethoverSrc('show-bthB')
        setPadding('main-container-padding-248')
        setWidth('width-85')
    }
}, [isIN]);

    const { data, isLoading, isError, error } = useQuery({
    queryKey: ['history-data'],
   queryFn: async () => {
      const res = await axios.get("http://localhost:5001/history/project_title");
      return res.data.History_data.map(item => ({
        id: item[0],
        title: item[1],
        folderId: item[2]
        }));
      }
    })

    if (isLoading) return <p>Loading...</p>;
    if (isError) return <p>{error.message}</p>;

    console.log("Fetched PDF URLs:", data);

  return (
    <>
        <div className='container'>
        <div className={`${isIN ? 'side-nav-in' : 'side-nav-out'}`}>
                <div className='top-container'>
                  <div className='search-nav-icon'>
                    <div className={`hide-show-bth ${hoverSrc}`} onClick={()=> setisIN(!isIN)}>
                      <img src={imageSrc} alt="Side-bar" className='icon'/>
                    </div>
                    <div className='search-icon show-bthB margin-left-100' onClick={() => setIsDialogOpen(true)}>
                      <img src={searchIcon} alt="search-Icon" className='icon'/>
                    </div>

                    <div className='search-icon show-bthB margin-left-5' onClick={()=> {navigate('/'), setActiveIndex(null)}}>
                      <img src={createIcon} alt="create-Icon" className='icon'/>
                    </div>

                  </div>
                </div>

                <div className='nav-item'>
                  <ul>
                      {data.map((project, index) => (
                        <li
                          key={project.id}
                          className={activeIndex === index ? 'active' : ''}
                          onClick={() => {
                            setActiveIndex(index);
                            navigate(`/new/project/home/${project.id}`);  // Navigate to dynamic route
                          }}
                        >
                          <a className={activeIndex === index ? 'active' : ''} href="#">
                            {project.title}
                          </a>
                        </li>
                      ))}
                  </ul> 
                </div>

                <div className='nav-item-bottom-icon'>
                    <img src={logo} alt="Logo" className="logo" />
                </div>
            </div>
            
            <Outlet context={{ padding, width }}/>

            {isDialogOpen && (
                <div className="dialog-overlay">
                    <div className="dialog-box">
                        <input type="search" placeholder='Search...'/>
                        <button onClick={() => setIsDialogOpen(false)} className="close-btn">Close</button>
                    </div>
                </div>
            )}

        </div>
        
        
    </>
  )
}

export default App
