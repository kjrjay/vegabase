function __FACTORY_NAME__(parentRoute: any) {
    return createRoute({
        getParentRoute: () => parentRoute,
        path: '__ROUTE_PATH__',
        component: function __COMPONENT_VAR__Wrapper() {
            const data = useLoaderData({ from: '__ROUTE_PATH__' });
            return <__COMPONENT_VAR__ {...data} />;
        },
        loader: async ({ context, params }) => {
            // During SSR, use ssrProps that were set before render
            if (ssrProps) {
                const props = ssrProps;
                ssrProps = null;  // Clear after use
                return props;
            }
            // During client-side navigation, fetch from backend
            const res = await fetch(__FETCH_PATH__, {
                headers: { 'X-Vegabase': 'true', 'Accept': 'application/json' },
                credentials: 'include'
            });
            const data = await res.json();
            return data.props;
        },
        __STALE_TIME__
    });
}
