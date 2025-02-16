import streamlit as st

if 'ssh_connection' not in st.session_state or not st.session_state['ssh_connection']:
    st.warning("Please connect to the Router first.")
else:
    st.header("Gateway Configuration")

    try:
        client = st.session_state.get('ssh_client', None)
        if client is None or client.get_transport() is None or not client.get_transport().is_active():
            st.error("SSH client is not available. Please reconnect.")
            st.stop()
        else:
            get_interface = "/interface print terse"
            stdin, stdout, stderr = client.exec_command(get_interface)
            output = stdout.read().decode().strip()

            interfaces = []
            for line in output.split("\n"):
                if "name=" in line:
                    interfaces.append(line.split("name=")[-1].split()[0])

            if not interfaces:
                st.error("No network interfaces found.")
                st.stop()

            selected_interface = st.selectbox("Select Interface (Connected to Internet):", interfaces)

            get_gateway = "/ip route print where dst-address=0.0.0.0/0"
            stdin, stdout, stderr = client.exec_command(get_gateway)
            gateway_output = stdout.read().decode().strip()
            stderr_output = stderr.read().decode().strip()

            if stderr_output:
                st.error(f"Error fetching current gateway: {stderr_output}")
                st.stop()

            current_gateway = None
            for line in gateway_output.split("\n"):
                if "gateway=" in line:
                    current_gateway = line.split("gateway=")[-1].split()[0]
                    break

            # Display current gateway info
            # st.write("### Current Gateway:")
            # st.info(f"🚀 **{current_gateway}**" if current_gateway else "No gateway configured.")

            # Input for new gateway
            new_gateway = st.text_input(
                "Enter New Gateway:", 
                placeholder="192.168.88.1",
                help="Example: 192.168.88.1 (Check with your network administrator)"
            )
            
            st.markdown("[What is gateway?](./pages/help.py)")

            replace_old = st.checkbox("Replace existing gateway", False)

            if st.button("Apply Gateway Configuration"):
                try:
                    if replace_old and current_gateway:
                        remove_command = f"/ip route remove [find gateway={current_gateway}]"
                        stdin, stdout, stderr = client.exec_command(remove_command)
                        stderr_output = stderr.read().decode().strip()
                        if stderr_output:
                            st.error(f"Error removing old gateway: {stderr_output}")
                        else:
                            st.warning(f"Previous gateway `{current_gateway}` removed.")

                    add_gateway_command = f"/ip route add dst-address=0.0.0.0/0 gateway={new_gateway}"
                    stdin, stdout, stderr = client.exec_command(add_gateway_command)
                    stderr_output = stderr.read().decode().strip()

                    if stderr_output:
                        st.error(f"Error adding new gateway: {stderr_output}")
                    else:
                        st.success(f"New gateway `{new_gateway}` applied successfully! 🚀")

                except Exception as e:
                    st.error(f"Failed: {e}")

    except Exception as e:
        st.error(f"Unexpected error: {e}")
