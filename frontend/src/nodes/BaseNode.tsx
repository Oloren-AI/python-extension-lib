import {
  Button,
  Input,
  InputNumber,
  Radio,
  Segmented,
  Select,
  Switch,
  Typography,
  Upload,
} from "antd";
import React, { useEffect, useRef, useState } from "react";
import { z } from "zod";
import {
  baseUrl,
  NodeSetter,
  type FlowNodeData,
  type Json,
  type NodeProps,
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
import { Bool, Choice, Num, Ty } from "../backend";

const dataSchema = z.array(z.any());

// define custom null value because data cannot be set to null
const nullValue = "SPECIALNULLVALUEDONOTSETEVER";

function RenderArgument({
  arg,
  callUpdate,
  argValue,
  setArg,
  setNode,
  idx: key,
}: {
  idx: number;
  arg: Ty;
  argValue: any;
  setArg: (newArg: any) => void;
  setNode: NodeSetter<any[]>;
  callUpdate: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);

  const [mode, setMode] = useState("node");

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

  return (
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
          setMode(newMode.toString());
          if (newMode !== "node") setArg(nullValue);
        }}
        options={[
          {
            icon: <LoginOutlined tw="pt-[3px]" />,
            value: "input",
          },
          {
            icon: <PlayCircleOutlined tw="pt-[3px]" />,
            value: "ui",
            disabled: true,
          },
          {
            icon: <PicCenterOutlined tw="pt-[3px]" />,
            value: "node",
            disabled: arg.type === "File",
          },
        ]}
      />
      <Typography.Text tw="w-fit">{arg.name}</Typography.Text>
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
          case "String":
            return (
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
  callAfterUpdateInpOuts = () => {},
  node,
  setNode,
}: NodeProps<z.infer<typeof dataSchema>>) {
  const data = dataSchema.safeParse(node.data).success
    ? (node.data as z.infer<typeof dataSchema>)
    : Array(node.metadata.args.length).fill(null);

  useEffect(() => {
    if(!dataSchema.length(node.metadata.args.length).safeParse(node.data).success){
      setNode((nd) => ({
        ...nd,
        data: Array(node.metadata.args.length).fill(null),
        operator: `${baseUrl(node.remote.url)}/operator/${
          node.metadata.operator
        }`, // specify operator url as such
        num_inputs: 0,
        num_outputs: node.metadata.num_outputs,
      }));
      callAfterUpdateInpOuts();
    }
  }, [node]);

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
          argValue={data[idx]}
          setNode={setNode}
          setArg={(newArg: any) => {
            setNode((nd) => ({
              ...nd,
              data: nd.data.map((x, i) => (i === idx ? newArg : x)),
            }));
          }}
        />
      ))}
    </div>
  );
}

export default BaseNode;
