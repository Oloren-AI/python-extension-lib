import { Config } from "./backend";
import { z } from "zod";

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
  metadata: Config;
  [key: string]: unknown;
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

// GRAPH Types

// Non Null JSON
const literalSchema = z.union([z.string(), z.number(), z.boolean()]);
type Literal = z.infer<typeof literalSchema>;
export const cloneJson = (json: Json): Json => JSON.parse(JSON.stringify(json));

export const jsonSchema: z.ZodType<Json> = z.lazy(() =>
  z.union([literalSchema, z.array(jsonSchema), z.record(jsonSchema)])
);

// Entry
export const entrySchema = z.object({
  id: z.number(),
  name: z.string().optional(),
  description: z.string().optional(),
});

export type Entry = z.infer<typeof entrySchema>;

// Node
export const nodeSchema = z.object({
  id: z.string(),
  operator: z.string(),
  input_ids: z.array(entrySchema),
  output_ids: z.array(entrySchema),
  data: jsonSchema,
  name: z.string().optional(),
  description: z.string().optional(),
});

export type Node = z.infer<typeof nodeSchema>;


export const graphSchema = z.array(nodeSchema);

export const graphNodeSchema = nodeSchema.extend({
  operator: z.enum(["graph"]),
  data: z.object({
    graph: graphSchema,
    data: jsonSchema,
  }),
});

export type GraphNode = z.infer<typeof graphNodeSchema>;
