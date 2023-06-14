import "twin.macro";
import styledImport, { CSSProp, css as cssImport } from "styled-components";
import { DOMAttributes } from "react";

declare module "twin.macro" {
  // The styled and css imports
  const styled: typeof styledImport;
  const css: typeof cssImport;
}

declare module "react" {
  // The css prop
  interface IntrinsicAttributes<T> extends DOMAttributes<T> {
    css?: CSSProp;
    tw?: string;
  }

  interface HTMLAttributes<T> extends IntrinsicAttributes<T>, DOMAttributes<T> {
    css?: CSSProp;
    tw?: string;
  }
  // The inline svg css prop
  interface SVGProps<T> extends SVGProps<SVGSVGElement> {
    css?: CSSProp;
    tw?: string;
  }
}

// The 'as' prop on styled components
declare global {
  namespace JSX {
    interface IntrinsicAttributes extends DOMAttributes<any> {
      as?: string;
    }
  }
}
