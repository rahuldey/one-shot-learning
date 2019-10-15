import React, { Fragment } from "react";

const Input = props => {
  return (
    <Fragment>
      <div className="custom-file mb-4">
        <input
          type="file"
          className="custom-file-input"
          onChange={props.onChange}
          id={props.id}
        />
        <label className="custom-file-label" htmlFor="customFile">
          {props.fileName}
        </label>
      </div>
    </Fragment>
  );
};

export default Input;
