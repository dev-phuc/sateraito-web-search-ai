import React from "react";
import { Link } from "react-router-dom";

const SidebarHeader = () => {
  return (
    <div className="sidebar-cta wrap-new-chat">
      <div className="d-flex ">
        {/* <strong className="d-inline-block mb-2">Monthly Sales Report</strong> */}
        {/* <div className="mb-3 text-sm">
          Your monthly sales report is ready for download!
        </div> */}

        <div className="d-flex new-chat-btn">
          {/* <a href="/conversation" className="btn btn-primary" rel="noreferrer">
            <i className="mdi mdi-plus"></i>
            New Chat
          </a> */}
          <Link to="/conversation" className="btn " rel="noreferrer">
            <i className="mdi mdi-chat-plus"></i>
            New Chat
          </Link>
        </div>
      </div>
    </div>
  );
};

export default SidebarHeader;
