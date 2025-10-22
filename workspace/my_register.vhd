library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

entity my_register is
    Port (
        clk      : in  STD_LOGIC;
        read     : in  STD_LOGIC;
        write    : in  STD_LOGIC;
        data_in  : in  STD_LOGIC_VECTOR(7 downto 0);
        data_out : out STD_LOGIC_VECTOR(7 downto 0)
    );
end my_register;

architecture Behavioral of my_register is
    signal reg : STD_LOGIC_VECTOR(7 downto 0);
begin
    process(clk)
    begin
        if rising_edge(clk) then
            if write = '1' then
                reg <= data_in;
            end if;
        end if;
    end process;

    data_out <= reg when read = '1' else (others => 'Z');
end Behavioral;
