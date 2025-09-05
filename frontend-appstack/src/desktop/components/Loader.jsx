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
const Loader = () => (
  <Container fluid className="vh-50 d-flex loader-component">
    <Helmet>
      <title>Loading... 🚀</title>
    </Helmet>

    <Row className="justify-content-center align-self-center w-100 text-center">
      <Spinner animation="border" />
    </Row>
  </Container>
);

export default Loader;
