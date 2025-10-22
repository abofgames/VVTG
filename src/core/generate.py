def make_copy(destination_path):
    """Generate testbench template directly without file dependency."""
    try:
        template = """library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity ENTITY_NAME_TB is
end ENTITY_NAME_TB;

architecture Behavioral of ENTITY_NAME_TB is
    -- Component declaration
    component ENTITY_NAME
        Port (
            clk : in STD_LOGICXPORTS
        );
    end component;

    -- Signals
    signal clk : STD_LOGIC := '0';
    XSIGNALS

    -- Configurable test parameters
    constant CLK_HIGH_TIME     : time := XHIGH_TIME ns;
    constant CLK_LOW_TIME      : time := XLOW_TIME ns;
    constant TEST_LENGTH       : time := XTEST_LENGTH ns;
    constant DATA_CHANGE_TIME  : time := XCHANGE_TIME ns;

begin
    -- Instantiate the Device Under Test (DUT)
    uut: ENTITY_NAME
        Port map(
            clk => clk
            XPORTMAP
        );

    -- Clock generation process
    clk_process : process
    begin
        while now < TEST_LENGTH loop
            clk <= '1';
            wait for CLK_HIGH_TIME;
            clk <= '0';
            wait for CLK_LOW_TIME;
        end loop;
        wait;
    end process;

    -- Stimulus process - applies test vectors
    stim_proc: process
    begin
        wait for 10 ns;

        XLOOP

        wait for 20 ns;
        assert false report "Simulation complete." severity note;
        wait;
    end process;

end Behavioral;
"""
        
        with open(destination_path + '.vhd', 'w') as file:
            file.write(template)
            
    except Exception as e:
        print(f"Error generating template: {e}")
        raise


def replace(file_path, old_string, new_string):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        updated_content = content.replace(old_string, new_string)

        with open(file_path, 'w') as file:
            file.write(updated_content)

    except Exception as e:
        print(f"Error processing file: {e}")

def time_loop(segments):
    pass