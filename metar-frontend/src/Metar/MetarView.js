import React, { useState, useEffect } from 'react';
import './MetarView.css';

function MetarView() {
  const [icao, setIcao] = useState('LOWW'); // Default ICAO code
  const [metarData, setMetarData] = useState(null);
  const [icaoCodes, setIcaoCodes] = useState([]);
  const API_KEY = process.env.REACT_APP_WEATHER_API_KEY; //Using enviroment variables.

  useEffect(() => {
      const fetchIcaoCodes = async () => {
        try {
          const apiUrl = window.REACT_APP_API_URL;
          const response = await fetch(`${apiUrl}/metar/airports`, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
              }
            });
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          const icaos = [];
          for (let i = 0; i < data.length; i++) {
            icaos[i] = data[i].icao;
          }
          setIcaoCodes(icaos);
        } catch (error) {
          console.error('Error fetching ICAO codes:', error);
        }
      };

      fetchIcaoCodes();
    }, []);
  
  useEffect(() => {
    const fetchMetar = async () => {
          try {
            const apiUrl = window.REACT_APP_API_URL;
            const response = await fetch(`${apiUrl}/metar/airports/weather/${icao}`, {
                method: 'GET',
                headers: {
                  'Content-Type': 'application/json',
                }
              });
            const data = await response.json();
            setMetarData(data);
          } catch (error) {
            console.error('Error fetching METAR data:', error);
          }
        };

        fetchMetar();
      }, [icao]);

  if (!metarData) {
    return <div>Loading METAR data...</div>;
  }
  
  const handleIcaoChange = (event) => {
    setIcao(event.target.value);
  };

  return (
    <div>
      <select value={icao} onChange={handleIcaoChange}>
        {icaoCodes.map((code) => (
          <option key={code} value={code}>
            {code}
          </option>
        ))}
      </select>
      {metarData ? (
        <div>
          <h2>This is the weather information for {metarData.icao}.</h2>
          <p>At <strong>{metarData.name}</strong> the temperature is reported with <strong>{metarData.temperature}°C</strong> and the dew point is <strong>{metarData.dewpoint}°C</strong>. 
          The humidity is <strong>{metarData.humidity}%</strong>. 
          The wind is coming from <strong>{metarData.wind_direction}</strong> at <strong>{metarData.wind_speed} knots</strong>. 
          The visibility is <strong>{metarData.visibility}m</strong>. The weather situation is <strong>{metarData.weather}</strong>.
          The air pressure is <strong>{metarData.qnh} hPa</strong>.
          </p>
        </div>
        ) : ("Not information available.")
      }    
    </div>
  );
}

export default MetarView;