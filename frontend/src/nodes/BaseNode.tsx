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
  Json as BackendJson,
  nullValue,
  Config,
} from "../backend";
import { NodeProps, NodeSetter } from "@oloren/core";

interface RenderArgumentProps {
  idx: number;
  arg: Ty;
  argValue: any;
  setArg?: (newArg: any) => void;
  setNode: NodeSetter<any[]>;
  callUpdate: () => void;
  optional?: boolean;
}

export function baseUrl(url: string) {
  const pathArray = url.split("/");
  const protocol = pathArray[0];
  const host = pathArray[2];
  return protocol + "//" + host;
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

  const mode = fullValue ? fullValue["mode"] : arg.type === "File" ? "input" : "node";

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
    if (!fullValue && (mode == "input" || optional) && setFullValue) {
      setArg(nullValue);
    }
  }, [fullValue, optional, mode, setFullValue]);

  type Handles = {
    [key: string]: number;
  };

  useEffect(() => {
    if (mode === "input" && ref.current && ref.current.offsetTop && ref.current.clientHeight) {
      console.log("OFFSET");
      setNode((nd) => {
        const newInputHandles: Handles = {
          ...(nd.input_handles ? nd.input_handles : {}),
          [key]: (ref.current?.offsetTop ?? 0) - 28,
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
            disabled: true,
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
          case "Json": {
            return null;
          }
          case "Bool":
            return (
              <Switch
                disabled={mode !== "node"}
                onChange={(newArg) => {
                  setArg(newArg);
                }}
                checked={argValue && argValue != nullValue ? argValue : (arg.ty as Bool).default}
              />
            );
          case "File":
            return null;
          case "Dir":
            return null;
          case "Func":
            return null;
          case "Funcs":
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

function BaseNode({ callAfterUpdateInpOuts = () => {}, node, setNode }: NodeProps<any[]>) {
  // @ts-expect-error
  const metadata = node.metadata! as Config & { lambda?: string };

  const initialized = Array.isArray(node.data) && node.data.length === metadata.args.length;
  const data = initialized ? (node.data as any[]) : Array(metadata.args.length).fill(null);

  useEffect(() => {
    if (!initialized) {
      setNode((nd) => ({
        ...nd,
        data: Array(metadata.args.length).fill(null),
        operator: metadata.lambda
          ? `${metadata.lambda}/operator/${metadata.operator}`
          : `${baseUrl(node.remote.url)}/operator/${metadata.operator}`,
        num_inputs: 0,
        num_outputs: metadata.num_outputs,
      }));
      callAfterUpdateInpOuts();
    }
  }, [node]);

  return (
    <div tw="flex flex-col space-y-2 w-96">
      {metadata.name ? <Typography.Text tw="font-bold">{metadata.name}</Typography.Text> : null}

      {metadata.description ? (
        <Typography.Paragraph>{metadata.description}</Typography.Paragraph>
      ) : null}

      {metadata.args.map((arg: any, idx: number) => (
        <RenderArgument
          arg={arg}
          key={idx}
          idx={idx}
          callUpdate={callAfterUpdateInpOuts}
          argValue={data[idx]}
          setNode={setNode}
          setArg={
            initialized
              ? (newArg: any) => {
                  setNode((nd) => ({
                    ...nd,
                    data: data.map((x, i) => (i === idx ? newArg : x)),
                  }));
                }
              : undefined
          }
        />
      ))}
    </div>
  );
}

export default BaseNode;
