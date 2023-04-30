export type Json = string | number | boolean | Json[] | { [key: string]: Json };

export interface FlowNodeData<T = Json> {
  id: string;
  data: T;
  num_inputs: number;
  num_outputs: number;
  operator: string;
  hierarchy: string[];
  special?: boolean;
  logs?: string;
  status?: "idle" | "running" | "finished" | "error";
  remote: {
    module: string;
    scope: string;
    url: string;
  };
}

export interface NodeProps<T = Json> {
  node: FlowNodeData<T>;
  setNode: NodeSetter<T>;
  callAfterUpdateInpOuts?: () => void;
}

export type NodeSetter<T = Json> = React.Dispatch<
  React.SetStateAction<FlowNodeData<T>>
>;

export function baseUrl(url: string) {
  const pathArray = url.split("/");
  const protocol = pathArray[0];
  const host = pathArray[2];
  return protocol + "//" + host;
}
