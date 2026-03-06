import mitt from "mitt";

export const EVENT_BUS_ACTION = {
  SHOW_LOADING: "show_loading",
} as const;

type EventBusEvents = {
  [EVENT_BUS_ACTION.SHOW_LOADING]: boolean;
};

const eventBusService = mitt<EventBusEvents>();

export default eventBusService;
