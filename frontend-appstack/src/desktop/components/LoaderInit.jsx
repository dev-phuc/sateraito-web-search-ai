import React from "react";
import { Container, Row, Spinner } from "react-bootstrap";
import { ReactComponent as Logo } from "@/assets/img/logo.svg";
import { ReactComponent as LogoH } from "@/assets/img/logo_horizontal.svg";

const LoaderInit = () => (
  // <Container fluid className="vh-50 d-flex">
  //   <Row className="justify-content-center align-self-center w-100 text-center">
  //     <Spinner animation="border" variant="primary" />
  //   </Row>
  // </Container>
  // <div className="wrap-loader">
  //   <div class="hm-spinner">
  //   </div>
  // </div>
  <div className="wrap-init-loader vertical-loaders">
    <Logo className="normal-logo v-loader" style={{ height: "80px" }} />
    <LogoH className="normal-logo h-loader" style={{ height: "200px" }} />
    <div className="linear-activity">
      <div className="indeterminate"></div>
    </div>
  </div>
);

export default LoaderInit;
