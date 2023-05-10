import {
  Button,
  Input,
  InputNumber,
  Popover,
  Radio,
  Segmented,
  Select,
  Switch,
  Tooltip,
  Typography,
  Upload,
} from "antd";
import React, { useEffect, useRef, useState } from "react";
import { z } from "zod";
import {
  baseUrl,
  NodeSetter,
  graphSchema,
  graphNodeSchema,
  type FlowNodeData,
  type Json,
  type NodeProps,
  type Node
} from "../util";
import {
  UploadOutlined,
  DownloadOutlined,
  LoginOutlined,
  PlayCircleOutlined,
  PicCenterOutlined,
} from "@ant-design/icons";
import { RcFile } from "antd/es/upload";
import "./style.css";
import "antd/dist/reset.css";
import {
  Bool,
  Choice,
  Num,
  Option,
  Ty,
  String as BackendString,
  nullValue,
} from "../backend";
// import uuid
import { v4 as uuidv4 } from "uuid";

const dataSchema = z.array(z.any());

interface RenderArgumentProps {
  idx: number;
  arg: Ty;
  argValue: any;
  setArg?: (newArg: any) => void;
  setNode: NodeSetter<any[]>;
  callUpdate: () => void;
  optional?: boolean;
}

function RenderArgument({
  arg,
  callUpdate,
  argValue: fullValue,
  setArg: setFullValue,
  setNode,
  idx: key,
  optional = false,
}: RenderArgumentProps) {
  const ref = useRef<HTMLDivElement>(null);

  const mode = fullValue
    ? fullValue["mode"]
    : arg.type === "File"
      ? "input"
      : "node";
  const argValue = fullValue ? fullValue["value"] : fullValue;

  const setArg = (newArg: any) => {
    if (setFullValue) setFullValue({ mode, value: newArg });
  };

  const setMode = (newMode: string) => {
    if (setFullValue) setFullValue({ mode: newMode, value: argValue });
  };

  const setBoth = (newMode: string, newArg: any) => {
    if (setFullValue) setFullValue({ mode: newMode, value: newArg });
  };

  useEffect(() => {
    if (!fullValue && optional && setFullValue) {
      setArg(nullValue);
    }
  }, [fullValue, optional, setFullValue]);

  type Handles = {
    [key: string]: number;
  };

  useEffect(() => {
    if (
      mode === "input" &&
      ref.current &&
      ref.current.offsetTop &&
      ref.current.clientHeight
    ) {
      setNode((nd) => {
        const newInputHandles: Handles = {
          ...(nd.input_handles ? nd.input_handles : {}),
          [key]:
            (ref.current?.offsetTop ?? 0) +
            (ref.current?.clientHeight ?? 0) / 2,
        };

        return {
          ...nd,
          input_handles: newInputHandles,
          num_inputs: Object.keys(newInputHandles).length,
        };
      });
      callUpdate();
    }
  }, [mode, ref]);

  useEffect(() => {
    if (mode === "node") {
      setNode((nd) => {
        const newInputHandles: Handles = {
          ...(nd.input_handles ? nd.input_handles : {}),
        };
        if (newInputHandles[key]) delete newInputHandles[key];
        return {
          ...nd,
          num_inputs: Object.keys(newInputHandles).length,
          input_handles: newInputHandles,
        };
      });
      callUpdate();
    }
  }, [mode]);

  return arg.type === "Option" ? (
    <RenderArgument
      arg={{
        name: arg.name,
        ty: (arg.ty as Option).inner,
        type: (arg.ty as Option)._type,
      }}
      callUpdate={callUpdate}
      argValue={fullValue}
      setArg={setFullValue}
      setNode={setNode}
      idx={key}
      optional={true}
    />
  ) : (
    <div className="flex flex-row space-x-2 items-center w-full" ref={ref}>
      <Segmented
        className="nodrag"
        onClick={(e) => {
          e.stopPropagation();
        }}
        tw="pointer-events-auto cursor-pointer"
        size={"small"}
        value={mode}
        onChange={(newMode) => {
          console.log(newMode)
          if (newMode === "node") setMode(newMode.toString());
          else setBoth(newMode.toString(), nullValue);
        }}
        options={[
          {
            label: (
              <Tooltip title="External Input">
                <LoginOutlined tw="pt-[3px]" />
              </Tooltip>
            ),
            value: "input",
          },
          {
            label: (
              <Tooltip title="UI Popup">
                <PlayCircleOutlined tw="pt-[3px]" />
              </Tooltip>
            ),
            value: "ui",
          },
          {
            label: (
              <Tooltip title="Hardcode">
                <PicCenterOutlined tw="pt-[3px]" />
              </Tooltip>
            ),
            value: "node",
            disabled: arg.type === "File",
          },
        ]}
      />
      <Typography.Text tw="w-fit whitespace-nowrap">
        {arg.name}
        {!optional ? <span style={{ color: "red" }}>*</span> : null}
      </Typography.Text>
      {(() => {
        switch (arg.type) {
          case "Choice":
            return (
              <Select
                tw="grow"
                className="nodrag"
                disabled={mode !== "node"}
                value={argValue && argValue != nullValue ? argValue : undefined}
                options={(arg.ty as Choice).choices.map((x: string) => ({
                  value: x,
                  label: x,
                }))}
                onChange={(newArg) => {
                  setArg(newArg);
                }}
              />
            );
          case "Num":
            return (
              <InputNumber
                tw="grow"
                className="nodrag"
                disabled={mode !== "node"}
                min={(arg.ty as Num).min_value ?? undefined}
                max={(arg.ty as Num).max_value ?? undefined}
                value={argValue && argValue != nullValue ? argValue : undefined}
                onChange={(newArg) => {
                  if (newArg) setArg(newArg);
                }}
              />
            );
          case "String": {
            return (arg.ty as BackendString).secret ? (
              <Input.Password
                tw="grow"
                className="nodrag"
                disabled={mode !== "node"}
                value={argValue && argValue != nullValue ? argValue : undefined}
                onChange={(e) => {
                  setArg(e.target.value);
                }}
              />
            ) : (
              <Input
                tw="grow"
                className="nodrag"
                disabled={mode !== "node"}
                value={argValue && argValue != nullValue ? argValue : undefined}
                onChange={(e) => {
                  setArg(e.target.value);
                }}
              />
            );
          }
          case "Bool":
            return (
              <Switch
                disabled={mode !== "node"}
                onChange={(newArg) => {
                  setArg(newArg);
                }}
                checked={
                  argValue && argValue != nullValue
                    ? argValue
                    : (arg.ty as Bool).default
                }
              />
            );
          case "File":
            return null;
          default: {
            const exhaustiveCheck: never = arg.type;
            throw new Error("Unhandled argument type");
          }
        }
      })()}
    </div>
  );
}

function BaseNode({
  callAfterUpdateInpOuts = () => { },
  node,
  setNode,
}: NodeProps<z.infer<typeof dataSchema>>) {
  console.log("BaseNode !!!", node)
  const [initialized, setInitialized] = useState(false);
  const [newId, setNewId] = useState<string>(uuidv4());

  useEffect(() => {
    console.log("BaseNode init")
    // check if node.data.data.operatorNode exists safely
    if (!node.data?.data?.operatorNode) {
      console.log("No op node")
      const newOpNode = {
        id: newId,
        operator: `${baseUrl(node.remote.url)}/operator/${node.metadata.operator
          }`, // specify operator url as such
        input_ids: [],
        output_ids: [],
        data: Array(node.metadata.args.length).fill(null)
      }
      console.log("newOpNode", newOpNode)
      setNode((nd) => ({
        ...nd,
        operator: "graph", // specify operator url as such
        num_inputs: 0,
        num_outputs: node.metadata.num_outputs,
        data: {
          data: {
            ...nd.data,
            operatorNode: newOpNode
          },
          graph: []
        }
      }));
    }
    setInitialized(true);
    console.log("BaseNode initialized")
  }, [node, initialized, setInitialized]);

  const [lastData, setLastData] = useState<any>(null);
  // set graph based on operator node
  useEffect(() => {
    if (initialized) {
      console.log("BaseNode changed")
      // if operator node is not set, do nothing
      if (!node.data?.data) return;
      if (!node.data.data?.operatorNode) return;

      // if the operator node has not changed, do nothing (check contents)
      if (JSON.stringify(node.data.data.operatorNode) === JSON.stringify(lastData)) return;
      console.log("BaseNode changed and not equal", node.data.data.operatorNode, lastData)
      // if the operator node has changed, update the graph
      setLastData(node.data.data.operatorNode);

      // newGraph as Array of Node
      let newGraph: Node[] = [];
      for (let i = 0; i < node.num_inputs; i++) {
        newGraph.push({
          id: node.id + "-input-" + i,
          operator: "proxyinnode",
          data: { index: i },
          input_ids: [],
          output_ids: [{ id: i }]
        })
      }

      let newOperatorNode = node.data.data.operatorNode;
      newOperatorNode.input_ids = Array(node.num_inputs).fill(null).map((_, i) => { return { "id": i } });
      newOperatorNode.output_ids = Array(node.num_outputs).fill(null).map((_, i) => { return { "id": i + node.num_inputs } });
      newGraph.push(newOperatorNode);

      for (let i = 0; i < node.num_outputs; i++) {
        newGraph.push({
          id: node.id + "-output-" + i,
          operator: "proxyoutnode",
          data: { id: i + node.num_inputs + 1 },
          input_ids: [{ id: i + node.num_inputs }],
          output_ids: [{id: i + node.num_inputs + node.num_outputs}]
        })
      }

      const newNode = {
        ...node,
        data: {
          graph: newGraph,
          data: {
            operatorNode: node.data.data.operatorNode
          }
        },
      }
      setNode((nd) => { return newNode })
    }
  }, [node, initialized]);

  console.log("Checking node", node)
  if (!node.data?.data) return null;
  if (!node.data.data?.operatorNode) return null;
  console.log("node is ", node)
  return (
    <div tw="flex flex-col space-y-2 w-96">
      {node.metadata.name ? (
        <Typography.Text tw="font-bold">{node.metadata.name}</Typography.Text>
      ) : null}

      {node.metadata.description ? (
        <Typography.Paragraph>{node.metadata.description}</Typography.Paragraph>
      ) : null}

      {node.metadata.args.map((arg: any, idx: number) => (
        <RenderArgument
          arg={arg}
          key={idx}
          idx={idx}
          callUpdate={callAfterUpdateInpOuts}
          argValue={node.data.data.operatorNode?.data[idx]}
          setNode={setNode}
          setArg={
            node.data.data.operatorNode
              ? (newArg: any) => {
                console.log("set arg", newArg);
                setNode((nd) => ({
                  ...nd,
                  data: {
                    ...nd.data,
                    data: {
                      operatorNode: {
                        ...nd.data.data.operatorNode,
                        data: nd.data.data.operatorNode.data.map((x, i) =>
                          i === idx ? newArg : x
                        ),
                      }
                    },
                  },
                }));
              }
              : (newArg: any) => { console.log("not initialized"); }
          }
        />
      ))}
    </div>
  );
}

export default BaseNode;
