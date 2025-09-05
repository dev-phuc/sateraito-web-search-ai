import React, { useEffect, useState } from "react";

import PerfectScrollbar from "react-perfect-scrollbar";
import { Button, OverlayTrigger, Tooltip } from "react-bootstrap";
import Offcanvas from "react-bootstrap/Offcanvas";

import useSidebar from "@/hooks/useSidebar";
import SidebarFooter from "./SidebarFooter";
import SidebarHeader from "./SidebarHeader";
import SidebarNav from "./SidebarNav";
import { ReactComponent as Logo } from "@/assets/img/logo.svg";
import { ReactComponent as LogoC } from "@/assets/img/logo_circle.svg";
import { useTranslation } from "react-i18next";
import { Link, useLocation } from "react-router-dom";
const renderTooltip = (title) => <Tooltip>{title}</Tooltip>;


const SidebarOffCanvas = ({ items, showFooter = true }) => {
  const { isOpen } = useSidebar();
  const { t } = useTranslation();
  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);
  const [show, setShow] = useState(false);

  let location = useLocation();
  useEffect(()=>{
    console.log("location.pathname=", location.pathname);
    setShow(false);
  }, [location])

  return (
    <>
        <OverlayTrigger
        placement="bottom"
        delay={{ show: 250, hide: 400 }}
        overlay={renderTooltip(t("PROMPT_BTN"))}
      >
        <Button
          type="button"
          data-id="prompt"
          variant=""
          className=" sidebar-toggle "
          onClick={handleShow}
          onKeyDown={(event) => {
            if (!event.shiftKey && event.key === "Enter") {
              handleShow(event);
            }
          }}
          tabIndex={4}
        >
          <i className="mdi mdi-menu  ico"></i>
        </Button>
      </OverlayTrigger>
      <Offcanvas
        className="offcanvas-prompt"
        placement="start"
        show={show}
        onHide={handleClose}
        // {...props}
      >
        <Offcanvas.Header closeButton>
          <Offcanvas.Title>
					<div className="wrap-header-static">
          <Link className="sidebar-brand" to="/" tabIndex={-1}>
            <Logo className="normal-logo" style={{ width: '100%' }} />
            <LogoC className="compact-logo" style={{ width: '100%' }} />

          </Link>
          {/* <SidebarHeader /> */}
        </div>
          </Offcanvas.Title>
        </Offcanvas.Header>
        <Offcanvas.Body className="">
        <div className="sidebar-content sidebar-custom">
        {/* <PerfectScrollbar>
          <Link className="sidebar-brand" to="/">
            <Logo />
          </Link>
          <SidebarHeader />
          <SidebarNav items={items} />
        </PerfectScrollbar> */}

        <SidebarNav items={items} />
      </div>
        </Offcanvas.Body>
      </Offcanvas>
      </>
  );
};

export default SidebarOffCanvas;
