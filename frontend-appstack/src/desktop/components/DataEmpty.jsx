// Framework import
import React from "react";
import { Helmet } from "react-helmet-async";

// Redux components

// Hook components

// Context components

// Library imports
// Library IU imports
import { Container, Row, Spinner } from "react-bootstrap";

// Define the component
const DataEmpty = ({ message }) => (
  <div className="d-flex justify-content-center align-items-center w-100 text-center" style={{ minHeight: 100 }}>
    {message ?
      <>{message} </>
      :
      <>Data Available</>
    }

  </div>
);

export default DataEmpty;
