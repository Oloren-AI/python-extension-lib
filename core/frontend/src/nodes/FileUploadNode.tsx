import { Button, Typography, Upload } from "antd";
import React, { useEffect, useState } from "react";
import { z } from "zod";
import type { FlowNodeData, Json, NodeProps } from "../util";
import { UploadOutlined, DownloadOutlined } from "@ant-design/icons";
import { RcFile } from "antd/es/upload";

const dataSchema = z.any();

function RemoteUI({
  outputs,
  setOutputs,
}: {
  inputs: Json[];
  node: FlowNodeData<z.infer<typeof dataSchema>>;
  outputs: (Json | File)[] | undefined;
  setOutputs: React.Dispatch<React.SetStateAction<(Json | File)[]>>;
}) {
  return (
    <div className="w-full flex flex-col space-y-2">
      <div>{outputs ? (outputs[0] as File).name : "No file uploaded"}</div>
      <Upload
        customRequest={({ file, onSuccess }) => {
          const f = file as RcFile;
          setOutputs([f]);
          if (onSuccess) onSuccess({});
        }}
      >
        <Button icon={<UploadOutlined />}>Upload File</Button>
      </Upload>
    </div>
  );
}

function DownloadFile({
  outputs,
  download,
}: {
  outputs: Json[];
  download?: (url: String) => void;
}) {
  const f = z
    .object({ reserved: z.literal("file"), url: z.string().url() })
    .parse(outputs[0]);

  return (
    <Button
      icon={<DownloadOutlined />}
      onClick={() => {
        if (download) download(f.url);
      }}
    >
      Download File
    </Button>
  );
}

function FileUploadNode({
  callAfterUpdateInpOuts = () => {},
  node,
  setNode,
}: NodeProps<z.infer<typeof dataSchema>>) {
  const data = dataSchema.parse(node.data);

  useEffect(() => {
    setNode((nd) => ({
      ...nd,
      data: {},
      operator: "ui",
      num_inputs: 0,
      num_outputs: 1,
      subcomponents: { ui: RemoteUI, output: DownloadFile },
    }));
    callAfterUpdateInpOuts();
  }, []);

  return (
    <div tw="flex flex-col space-y-2">
      <Typography.Text>File Upload</Typography.Text>
    </div>
  );
}

export default FileUploadNode;
