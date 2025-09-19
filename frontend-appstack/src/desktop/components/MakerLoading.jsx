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
const MakerLoading = ({ message, opacity }) => (
  <div className={
    `position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-white` +
    (opacity !== undefined ? ` bg-opacity-${opacity}` : ` bg-opacity-75`)
  }>
    <div className="text-center">
      <Spinner animation="border" variant="primary" />
      {message && (
        <div className="mt-2 text-muted small">{message}</div>
      )}
    </div>
  </div>
);

export default MakerLoading;
