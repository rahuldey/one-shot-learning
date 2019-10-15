import React from "react";
import PropTypes from "prop-types";

const Message = ({ msg }) => {
  return (
    <div>
      <div className="alert alert-info alert-dismissible" role="alert">
        <button
          type="button"
          className="close"
          data-dismiss="alert"
          aria-label="Close"
        >
          <span aria-hidden="true">&times;</span>
        </button>
        {msg}
      </div>
    </div>
  );
};

Message.propTypes = {
  msg: PropTypes.string.isRequired
};

export default Message;
