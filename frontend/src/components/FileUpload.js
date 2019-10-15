import React, { Fragment, useState } from "react";
import axios from "axios";
import Input from "./Input";
import Message from "./Message";

const FileUpload = () => {
  const [firstFile, setFirstFile] = useState("");
  const [firstFileName, setFirstFileName] = useState("Choose File");
  const [secondFile, setSecondFile] = useState("");
  const [secondFileName, setSecondFileName] = useState("Choose File");

  const [responseMessage, setResponseMessage] = useState("");

  const mapHandlers = {
    first: [setFirstFile, setFirstFileName],
    second: [setSecondFile, setSecondFileName]
  };

  const onChange = e => {
    if (!e.target.files[0]) return;
    mapHandlers[e.target.id][0](e.target.files[0]);
    mapHandlers[e.target.id][1](e.target.files[0].name);
  };

  const onSubmit = async e => {
    e.preventDefault();
    if (isIncomplete()) {
      return;
    }

    setResponseMessage("");

    const formData = new FormData();
    formData.append("firstFile", firstFile);
    formData.append("secondFile", secondFile);

    try {
      const res = await axios.post("http://localhost:5000/predict", formData, {
        "Content-Type": "multipart/form-data"
      });
      console.log("Submitted");
      console.log(res);
      setResponseMessage(res.data.response);
    } catch (err) {
      if (err.response.status === 500) {
        setResponseMessage("There was a problem with the server");
      } else {
        setResponseMessage(err.response.data.response);
      }
    }
  };

  const isIncomplete = () => firstFile === "" || secondFile === "";

  return (
    <Fragment>
      {responseMessage ? <Message msg={responseMessage} /> : null}
      <form onSubmit={onSubmit}>
        <Input fileName={firstFileName} onChange={onChange} id="first" />
        <Input fileName={secondFileName} onChange={onChange} id="second" />
        <input
          type="submit"
          value="upload"
          className="btm btn-primary btn-block mt-4"
        />
      </form>
    </Fragment>
  );
};

export default FileUpload;
