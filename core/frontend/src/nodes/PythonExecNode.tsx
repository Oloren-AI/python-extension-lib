import { Select, Typography, Input, Modal } from "antd";
import { FloatButton } from "antd";
import { QuestionCircleOutlined } from "@ant-design/icons";
import React, { useEffect, useState } from "react";
import { z } from "zod";

import * as monaco from "monaco-editor";
import Editor, { loader } from "@monaco-editor/react";

loader.config({ monaco });
const { Text, Paragraph } = Typography;

import { NodeProps, baseUrl, Json } from "../util";

export default function PythonExecNode({
  callAfterUpdateInpOuts = () => {},
  node,
  setNode,
}: NodeProps) {
  const defaultInputLabels = Array(node.num_inputs).fill("");
  const defaultOutputLabels = Array(node.num_outputs).fill("");
  const defaultSourceCode = "# comment";

  const nodeDataSchema = z.object({
    inputLabels: z.array(z.string()).default(defaultInputLabels),
    outputLabels: z.array(z.string()).default(defaultOutputLabels),
    sourceCode: z.string().default(defaultSourceCode),
  });

  const nodeDataParse = nodeDataSchema.safeParse(node.data);
  let nodeData: z.infer<typeof nodeDataSchema> = nodeDataParse.success
    ? nodeDataParse.data
    : {
        inputLabels: defaultInputLabels,
        outputLabels: defaultOutputLabels,
        sourceCode: defaultSourceCode,
      };

  if (nodeData.inputLabels.length !== node.num_inputs)
    nodeData.inputLabels = defaultInputLabels;
  if (nodeData.outputLabels.length !== node.num_outputs)
    nodeData.outputLabels = defaultOutputLabels;

  const [isModalVisible, setIsModalVisible] = useState(false);

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleOk = () => {
    setIsModalVisible(false);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
  };

  useEffect(() => {
    if (node.operator !== `${baseUrl(node.remote.url)}/operator/python_eval`) {
      setNode((nd) => ({
        ...nd,
        data: {},
        operator: `${baseUrl(node.remote.url)}/operator/python_eval`, // specify operator url as such
      }));
    }
  }, []);

  // ... (rest of the code remains the same)

  return (
    <div className="nodrag">
      <FloatButton
        onClick={showModal}
        icon={<QuestionCircleOutlined />}
        type="primary"
        style={{ right: 24, bottom: 24 }}
      />
      <Modal
        title="Info"
        open={isModalVisible}
        onOk={handleOk}
        onCancel={handleCancel}
      >
        <p>
          You can name input arguments and output values in the provided fields.
          Then, use these names in your Python code within the Editor as
          variable names and those variables will be mapped to their respective
          input values and output slots.
        </p>
        <p>
          The Python code will be executed using the "exec" function. To add
          more inputs or outputs, click the edge of the node and click +/- at
          the handles.
        </p>
      </Modal>

      <div tw="flex flex-row space-x-4 items-center">
        <Text>Python RDKit Exec Node: </Text>
        <div tw="grid grid-cols-2 gap-4 py-4">
          <div tw="grid grid-cols-1 bg-gray-100 m-4">
            {Array(node.num_inputs)
              .fill(0)
              .map((_, index) => (
                <div key={index} tw="m-4">
                  <Paragraph>
                    {index + 1}: Variable Name (input string field)
                  </Paragraph>
                  <Input
                    autoComplete="off"
                    value={nodeData.inputLabels[index]}
                    onChange={(e) => {
                      setNode((nd) => ({
                        ...nd,
                        data: {
                          ...nodeData,
                          inputLabels: nodeData.inputLabels.map((v, i) =>
                            i === index ? e.target.value : v
                          ),
                        },
                      }));
                    }}
                    placeholder={`Enter variable name for input ${index + 1}`}
                  />
                </div>
              ))}
          </div>
          <div tw="grid grid-cols-1 bg-gray-100 m-4">
            {Array(node.num_outputs)
              .fill(0)
              .map((_, index) => (
                <div key={index} tw="m-4">
                  <Paragraph>
                    {index + 1}: Variable Name (output string field)
                  </Paragraph>
                  <Input
                    autoComplete="off"
                    value={nodeData.outputLabels[index]}
                    onChange={(e) => {
                      setNode((nd) => ({
                        ...nd,
                        data: {
                          ...nodeData,
                          outputLabels: nodeData.outputLabels.map((v, i) =>
                            i === index ? e.target.value : v
                          ),
                        },
                      }));
                    }}
                    placeholder={`Enter variable name for output ${index + 1}`}
                  />
                </div>
              ))}
          </div>
        </div>
      </div>
      <Editor
        height="800px"
        width="100%"
        defaultLanguage="python"
        value={nodeData.sourceCode}
        onChange={(v, e) => {
          // check if undefined
          if (v)
            setNode((nd) => ({
              ...nd,
              data: {
                ...nodeData,
                sourceCode: v,
              },
            }));
        }}
      />
    </div>
  );
}
