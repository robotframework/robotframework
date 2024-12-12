type Libdoc = {
  specversion: number;
  name: string;
  doc: string;
  version: string;
  generated: string;
  type: string;
  scope: string;
  docFormat: string;
  source: string;
  lineno: number;
  tags: Array<string>;
  inits: Array<Keyword>;
  keywords: Array<Keyword>;
  typedocs: Array<TypeDoc>;
  theme: string | null;
  lang: string | null;
};

type Keyword = {
  name: string;
  args: Array<Arg>;
  returnType: ArgType | null;
  doc: string;
  shortdoc: string;
  tags: Array<string>;
  source: string;
  lineno: number;
  deprecated?: boolean;
};

type Arg = {
  name: string;
  type: ArgType | null;
  defaultValue: string | null;
  kind:
    | "NAMED_ONLY"
    | "NAMED_ONLY_MARKER"
    | "POSITIONAL_OR_NAMED"
    | "VAR_POSITIONAL";
  required: boolean;
  repr: string;
};

type ArgType = {
  name: string;
  typedoc: string | null;
  nested: Array<ArgType>;
  union: boolean;
};

type TypeDoc = {
  type: string;
  name: string;
  doc: string;
  usages: Array<string>;
  accepts: Array<string>;
  members?: Array<TypeMember>;
  items?: Array<TypeItem>;
};

type TypeMember = {
  name: string;
  value: string;
};

type TypeItem = {
  key: string;
  type: string;
  required: boolean;
};

interface RuntimeLibdoc extends Libdoc {
  selectedTag?: string;
  inits: Array<RuntimeKeyword>;
  keywords: Array<RuntimeKeyword>;
}

interface RuntimeKeyword extends Keyword {
  hidden?: boolean;
}
